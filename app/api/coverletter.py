from fastapi import FastAPI, APIRouter, HTTPException, Depends
from pydantic import BaseModel
from langchain import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from .upload_transcript_cv import OPENAI_API_KEY
from app import database, models, schemas
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.schemas import CoverLetterRequest


app = FastAPI()
router = APIRouter()

# Initialize the OpenAI API

openai = OpenAI(api_key="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")

#Define the prompt template for generating the cover letter
prompt_template = PromptTemplate(
    input_variables=["cv", "job_description"],
    template=(
        "Using the following curriculum vitae (CV) and job description, generate a cover letter. \n\n"
        "avoid using '[' as this will be a final product that will be directly passed to hr. Be human!"
        "CV:\n{cv}\n\n"
        "Job Description:\n{job_description}\n\n"
        "Cover Letter:\n"
    ),
)

# Initialize the LLMChain with the OpenAI LLM and the prompt template
llm_chain = LLMChain(
    llm=openai,
    prompt=prompt_template
)

@router.post("/coverletter")
async def generate_cover_letter(request: schemas.CoverLetterRequest, db: Session = Depends(database.get_db)):
    # Query the database for the user's CV text
    user_cv = db.query(models.Cv).filter(models.Cv.user_id == request.user_id).order_by(desc(models.Cv.created_at)).first()
    print(f"user_cv id: {user_cv.id}, user_id: {user_cv.user_id}, text_pdf: {user_cv.text_pdf}")
    if not user_cv:
        raise HTTPException(status_code=404, detail="CV not found for the user")
    
    # Extract the text_pdf (transcribed CV text)
    cv_text = user_cv.text_pdf

    try:
        # Use LangChain to generate the cover letter
        result = llm_chain.invoke({
            "cv": cv_text,
            "job_description": request.jobDescription
        })
        return {"cover_letter": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the FastAPI app
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)