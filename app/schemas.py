from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CvOut(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    default_cv: Optional[bool]
    user_id: int
    title: Optional[str]
    pdf_path: str
    text_pdf: str


class CvPatch(BaseModel):
    title: Optional[str] = None
    # pdf_path: Optional[str] = None
    # text_pdf: Optional[str] = None
    default_cv: Optional[bool] = None


class CVBase(BaseModel):
    user_id: int
    pdf_path: str


class CVCreate(CVBase):
    text_pdf: str
    pdf_path: str
    default_cv: Optional[bool]


class CV(CVBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# class CoverLetterRequest(BaseModel):
#     user_id: int
#     jobDescription: str
class CoverLetterRequest(BaseModel):
    jobDescription: str


class CoverLettersOut(BaseModel):
    id: int
    user_id: int
    cv_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    title: str
    poster: Optional[str]


class CoverLetterOut(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    title: str
    cv_id: int
    poster: Optional[str]
    text: str


class CoverLetterPatch(BaseModel):
    title: Optional[str] = None
    poster: Optional[str] = None
    text: Optional[str] = None
