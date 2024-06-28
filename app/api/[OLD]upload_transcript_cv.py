from fastapi import APIRouter, Depends
from fastapi import File, UploadFile, Depends, HTTPException
from pathlib import Path

from fastapi.params import Query
from app import models, schemas, crud, database
from sqlalchemy.orm import Session
import base64
import requests
from app.util import convert_to_base64_from_pdf
import fitz
from sqlalchemy import desc
from typing import Optional
from ..utils import transcribe_file


OPENAI_API_KEY = "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"

router = APIRouter(prefix="/cvs", tags=["CV"])

# NOTE EDGE CASE: Bisgna aggiungere il caso in cui il cv ha più pagine!!!!


@router.post("", response_model=schemas.CvOut)
async def upload_and_transcript(
    # user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    default_cv: Optional[bool] = Query(False),
):

    user = db.query(models.User).filter(models.User.id == "1").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    file_location = Path("uploaded_files") / file.filename

    # base64_image = convert_to_base64_from_pdf(file_location, file)

    # # Convert PDF to image using PyMuPDF
    # doc = fitz.open(file_location)
    # page = doc.load_page(0)  # get the first page -> qui come per più pagine?
    # pix = page.get_pixmap()  # render page to an image
    # image_path = file_location.with_suffix(".png")
    # pix.save(image_path)

    # # Read the image file to base64
    # with open(image_path, "rb") as img_file:
    #     base64_image = base64.b64encode(img_file.read()).decode("utf-8")

    # headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": f"Bearer {OPENAI_API_KEY}",
    # }

    # payload = {
    #     "model": "gpt-4o",
    #     "messages": [
    #         {
    #             "role": "user",
    #             "content": [
    #                 {
    #                     "type": "text",
    #                     "text": "Transcribe the following curriculum vitae (CV) from the provided image. "
    #                     "Extract and format the text clearly, maintaining the structure of the CV. Include headings such as "
    #                     "Personal Information, Education, Work Experience, Skills, and any other relevant sections. Ensure that all "
    #                     "dates, job titles, and descriptions are accurately transcribed. "
    #                     "IMPORTANT: Only provide the transcribed text. Do not include any additional commentary or text.\n\n"
    #                     "Here is the image:",
    #                 },
    #                 {
    #                     "type": "image_url",
    #                     "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
    #                 },
    #             ],
    #         }
    #     ],
    #     "max_tokens": 1500,
    # }

    # response = requests.post(
    #     "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    # )
    # response_data = response.json()
    # print(response_data)

    # extracted_text = (
    #     response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
    # )
    # print("extracted text: " + extracted_text)

    extracted_text = transcribe_file(file, file_location)

    cv_data = schemas.CVCreate(
        user_id="1", pdf_path=str(file_location), text_pdf=extracted_text
    )

    db_cv = crud.create_cv(db=db, cv=cv_data)
    return db_cv
