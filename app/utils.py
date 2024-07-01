# from pathlib import Path
from fastapi import HTTPException, UploadFile
from pathlib import Path

import requests
from openai import OpenAI
from app.prompt import cover_letter_guidelines_sys_prompt
import fitz
import shutil
import base64


OPENAI_API_KEY = "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"
client = OpenAI(
    # This is the default and can be omitted
    api_key="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"
)


def convert_to_base64_from_pdf(
    file,
    file_location,
):
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert PDF to image using PyMuPDF
    doc = fitz.open(file_location)
    page = doc.load_page(0)  # get the first page
    pix = page.get_pixmap()  # render page to an image
    image_path = file_location.with_suffix(".png")
    pix.save(image_path)

    # Read the image file to base64
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode("utf-8")
    return base64_image


# agiungere file tipe
async def transcribe_file(file: UploadFile, file_location: Path):
    # file_location = Path("uploaded_files") / file.filename

    base64_image = convert_to_base64_from_pdf(file, file_location)

    # Convert PDF to image using PyMuPDF
    doc = fitz.open(file_location)
    page = doc.load_page(0)  # get the first page -> qui come per più pagine?
    pix = page.get_pixmap()  # render page to an image
    image_path = file_location.with_suffix(".png")
    pix.save(image_path)

    # Read the image file to base64
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Transcribe the following curriculum vitae (CV) from the provided image. "
                        "Extract and format the text clearly, maintaining the structure of the CV. Include headings such as "
                        "Personal Information, Education, Work Experience, Skills, and any other relevant sections. Ensure that all "
                        "dates, job titles, and descriptions are accurately transcribed. "
                        "IMPORTANT: Only provide the transcribed text. Do not include any additional commentary or text.\n\n"
                        "Here is the image:",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": 1500,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    response_data = response.json()
    # print(response_data)

    extracted_text = (
        response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
    )
    # print("extracted text: " + extracted_text)
    return extracted_text


# Define the prompt template for generating the cover letter
def generate_prompt(cv: str, job_description: str) -> str:
    return (
        "Using the following curriculum vitae (CV) and job description, generate a cover letter. \n"
        f"CV:\n{cv}\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Cover Letter:\n"
    )


# agiungere typing
async def generate_cover_letter(cv_text: str, job_description: str):
    try:
        # Generate the prompt
        prompt = generate_prompt(cv_text, job_description)

        # Call the OpenAI API to generate the cover letter
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": cover_letter_guidelines_sys_prompt,
                },
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o",
        )
        #  print (response.choices[0].message.content.strip())
        # Extract the cover letter from the response
        # cover_letter = response.choices[0].message.content.strip()
        # Extract the cover letter from the response
        cover_letter_text = response.choices[0].message.content.strip()

        return cover_letter_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
