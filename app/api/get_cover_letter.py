
from fastapi import APIRouter, Depends, HTTPException

from app import models,  database
from sqlalchemy.orm import Session

from sqlalchemy import desc

router = APIRouter()

@router.get("/coverletter/{user_id}")
async def get_cover_letter(user_id: int, db: Session = Depends(database.get_db)):
    # Query the database for the user's cover letter
    user_cover_letter = db.query(models.Coverletter).filter(models.Coverletter.user_id == user_id).order_by(desc(models.CoverLetter.created_at)).first()
    if not user_cover_letter:
        raise HTTPException(status_code=404, detail="Cover letter not found for the user")
    
    return {"cover_letter": user_cover_letter.text}
