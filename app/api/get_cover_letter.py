
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app import models,  database
from sqlalchemy.orm import Session

from sqlalchemy import desc

router = APIRouter()

@router.get("/coverletter/{user_id}")
async def get_cover_letter(user_id: int, db: Session = Depends(database.get_db)):
    print("#########")
    try:
        print("#########")
        user_cover_letter = db.query(models.Coverletter).filter(models.Coverletter.user_id == user_id).order_by(desc(models.Coverletter.created_at)).first()
        if user_cover_letter is None:
            print(f"No cover letter found for user_id: {user_id}")
        if not user_cover_letter:
            raise HTTPException(status_code=404, detail="Cover letter not found for the user")
        return {"cover_letter": user_cover_letter.text}
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")
