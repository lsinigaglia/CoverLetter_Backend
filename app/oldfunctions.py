from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from api.oauth2 import router as oauth2_router

from .init_db import init_db
import shutil
from pathlib import Path
from . import models, schemas, crud, database
from sqlalchemy.orm import Session
import pdfplumber


app = FastAPI()
OPENAI_API_KEY="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"

#init_db()


from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
from pathlib import Path
import pdfplumber
from . import models, schemas, crud, database

app = FastAPI()

def save_uploaded_file(upload_file: UploadFile) -> Path:
    """Save upload file to disk."""
    try:
        destination = Path("uploaded_files") / upload_file.filename
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return destination
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF file."""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {e}")

@app.post("/upload_cv/", response_model=schemas.CV)
async def upload_and_transcript_cv(user_id: int, file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    file_location = save_uploaded_file(file)

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(file_location)

    # Create a new CV record
    cv_data = schemas.CVCreate(
        user_id=user_id,
        pdf_path=str(file_location),
        text_pdf=extracted_text
    )
    db_cv = crud.create_cv(db=db, cv=cv_data)
    return db_cv




@app.get("/extract_cv/")




async def root():
    return {"message": "Hello World"}
# Include the OAuth2 router
app.include_router(oauth2_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)