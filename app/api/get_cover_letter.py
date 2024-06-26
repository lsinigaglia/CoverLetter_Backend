
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError

from app import models,  database
from sqlalchemy.orm import Session

from sqlalchemy import desc

router = APIRouter()

@router.get("/coverletter/{user_id}")
async def get_cover_letter(user_id: int, db: Session = Depends(database.get_db)):
    start_time = time.time()
    print("Start processing request")

    try:
        query_start_time = time.time()
        user_cover_letter = db.query(models.Coverletter).filter(models.Coverletter.user_id == user_id).order_by(desc(models.Coverletter.created_at)).first()
        query_end_time = time.time()
        print(f"Query execution time: {query_end_time - query_start_time:.4f} seconds")

        if user_cover_letter is None:
            print(f"No cover letter found for user_id: {user_id}")
            raise HTTPException(status_code=404, detail="Cover letter not found for the user")

        end_time = time.time()
        print(f"Total execution time: {end_time - start_time:.4f} seconds")

        return {"cover_letter": user_cover_letter.text}
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")
    
def create_preview(text, word_limit=25):
    words = text.split()
    return " ".join(words[:word_limit])

@router.get("/coverletters/{user_id}")
async def get_cover_letters(user_id: int, db: Session = Depends(database.get_db), limit: int = Query(40, ge=1), skip: int = Query(0, ge=0)):
    start_time = time.time()
    print("Start processing request")

    try:
        query_start_time = time.time()
        cover_letters_query = db.query(models.Coverletter).filter(models.Coverletter.user_id == user_id).order_by(desc(models.Coverletter.created_at)).limit(limit).offset(skip)
        
        query_end_time = time.time()
        print(f"Query execution time: {query_end_time - query_start_time:.4f} seconds")
        cover_letters = cover_letters_query.all()

        
        
        if not cover_letters:
            print(f"No cover letters found for user_id: {user_id}")
            raise HTTPException(status_code=404, detail="Cover letters not found for the user")

        cover_letter_list = []
        for cover_letter in cover_letters:
            preview_text = ' '.join(cover_letter.text.split()[:20])  
            cover_letter_list.append({
                'id': cover_letter.id,
                'title': cover_letter.title,
                'poster': cover_letter.poster,  
                'preview': preview_text
            })

        end_time = time.time()
        print(f"Total execution time: {end_time - start_time:.4f} seconds")
        
        return cover_letter_list

    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")