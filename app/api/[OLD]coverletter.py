from fastapi import FastAPI, APIRouter, HTTPException, Depends
from app.util import coverLetterGuidelinesSysPrompt
from app import database, models, schemas
from sqlalchemy.orm import Session
from sqlalchemy import desc
from openai import OpenAI


app = FastAPI()
router = APIRouter(prefix="/coverletters", tags=["Cover Letters"])

# Initialize the OpenAI API

client = OpenAI(
    # This is the default and can be omitted
    api_key="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"
)


# Define the prompt template for generating the cover letter
def generate_prompt(cv: str, job_description: str) -> str:
    return (
        "Using the following curriculum vitae (CV) and job description, generate a cover letter. \n"
        f"CV:\n{cv}\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Cover Letter:\n"
    )


@router.post("", response_model=schemas.CoverLetterOut)
async def create_cover_letter(
    request: schemas.CoverLetterRequest, db: Session = Depends(database.get_db)
):
    # Query the database for the user's CV text
    user_cv = (
        db.query(models.Cv)
        # .filter(models.Cv.user_id == request.user_id)
        .filter(models.Cv.user_id == "1")
        # qui mettiamo un filtro che sceglie il cv cha ha default == true
        .filter(models.Cv.id == "1")
        # .order_by(desc(models.Cv.created_at))
        .first()
    )
    if not user_cv:
        raise HTTPException(status_code=404, detail="CV not found for the user")

    # Extract the text_pdf (transcribed CV text)
    cv_text = user_cv.text_pdf
    # print ("ciao")
    try:
        # Generate the prompt
        prompt = generate_prompt(cv_text, request.jobDescription)

        # Call the OpenAI API to generate the cover letter
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": coverLetterGuidelinesSysPrompt},
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o",
        )
        #  print (response.choices[0].message.content.strip())
        # Extract the cover letter from the response
        # cover_letter = response.choices[0].message.content.strip()
        # Extract the cover letter from the response
        cover_letter_text = response.choices[0].message.content.strip()
        # print(cover_letter_text)

        # Create a new Coverletter instance and save to the database
        new_cover_letter = models.Coverletter(
            text=cover_letter_text,
            title="COVER LETTER AMAZON TEST",  # You might want to add a title field in your request schema or generate it differently
            user_id="1",
        )
        db.add(new_cover_letter)
        db.commit()

        # return {"cover_letter": cover_letter_text}
        return new_cover_letter
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
