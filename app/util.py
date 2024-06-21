import fitz
import shutil
import base64
from fastapi import File

def convert_to_base64_from_pdf(file_location, file):
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert PDF to image using PyMuPDF
    doc = fitz.open(file_location)
    page = doc.load_page(0)  # get the first page
    pix = page.get_pixmap()  # render page to an image
    image_path = file_location.with_suffix('.png')
    pix.save(image_path)

    # Read the image file to base64
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode("utf-8")
    return base64_image