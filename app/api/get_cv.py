
from fastapi import APIRouter, Depends, HTTPException

from app import models,  database
from sqlalchemy.orm import Session

from sqlalchemy import desc

router = APIRouter()

@router.get("/cv/{user_id}")
async def get_cv(user_id: int, db: Session = Depends(database.get_db)):
    # Query the database for the user's CV
    user_cv = db.query(models.Cv).filter(models.Cv.user_id == user_id).order_by(desc(models.Cv.created_at)).first()
    if not user_cv:
        raise HTTPException(status_code=404, detail="CV not found for the user")
    
    return {"cv_text": user_cv.text_pdf}
