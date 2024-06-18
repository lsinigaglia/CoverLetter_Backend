from pydantic import BaseModel
from datetime import datetime

class CVBase(BaseModel):
    user_id: int
    pdf_path: str

class CVCreate(CVBase):
    text_pdf: str


class CV(CVBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CoverLetterRequest(BaseModel):
    user_id: int
    jobDescription: str