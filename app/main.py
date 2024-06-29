from fastapi import FastAPI
from app.api.oauth2 import router as oauth2_router
from fastapi.middleware.cors import CORSMiddleware

# from app.api.upload_transcript_cv import router as upload_transcript_cv_router
# from app.api.coverletter import router as cover_letter_router
# from app.api.get_cover_letter import router as get_cover_letter_router
# from app.api.get_cv import router as get_cv_router
from app.api.cv import router as cv_router
from app.api.cover_letter import router as cover_letter_router

from app.init_db import init_db


app = FastAPI()

# init_db()

origins = [
    # "http://localhost", "http://localhost:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# app.include_router(oauth2_router)
# app.include_router(cover_letter_router)
# app.include_router(get_cover_letter_router)
# app.include_router(upload_transcript_cv_router)
# app.include_router(get_cv_router)
app.include_router(cv_router)
app.include_router(cover_letter_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
