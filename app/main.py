from fastapi import FastAPI
from app.api.oauth2 import router as oauth2_router
from app.api.upload_transcript_cv import router as upload_transcript_cv_router
from app.api.coverletter import router as cover_letter_router
from app.init_db import init_db


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