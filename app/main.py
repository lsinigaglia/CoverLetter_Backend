from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from app.api.oauth2 import router as oauth2_router
from app.api.upload_transcript_cv import router as upload_transcript_cv_router
from app.api.coverletter import router as cover_letter_router
from fastapi.responses import JSONResponse
from app.init_db import init_db
import shutil
from pathlib import Path
from . import models, schemas, crud, database
from sqlalchemy.orm import Session
from openai import OpenAI
import fitz  # PyMuPDF

from PIL import Image
from pdf2image import convert_from_path
from io import BytesIO

import pdfplumber

import base64
import requests

app = FastAPI()

#init_db()

async def root():
    return {"message": "Hello World"}
# Include the OAuth2 router
app.include_router(oauth2_router)
app.include_router(upload_transcript_cv_router)
app.include_router(cover_letter_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)