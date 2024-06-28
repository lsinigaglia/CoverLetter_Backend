import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError

from app import models, database
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas
from ..utils import generate_cover_letter

from sqlalchemy import desc, case, func

router = APIRouter(prefix="/coverletters", tags=["Cover Letters"])


# userid: 1
# Get list of cover letters
@router.get(
    "",
    response_model=List[schemas.CoverLettersOut],
)
async def get_cover_letters(
    # user_id: int,
    db: Session = Depends(database.get_db),
    # limit: int = Query(40, ge=1),
    # skip: int = Query(0, ge=0),
):
    # start_time = time.time()
    # print("Start processing request")

    try:
        # query_start_time = time.time()

        cover_letters = (
            db.query(models.Coverletter)
            .filter(
                models.Coverletter.user_id == "1"
            )  # Replace 1 with the actual user_id variable
            .order_by(
                # va testata la performance di questo order by -> lho testata è identica
                desc(
                    func.coalesce(
                        models.Coverletter.updated_at, models.Coverletter.created_at
                    )
                )
            )
            .all()
        )

        # query_end_time = time.time()
        # print(f"Query execution time: {query_end_time - query_start_time:.4f} seconds")
        # cover_letters = cover_letters_query.all()

        if not cover_letters:
            print(f"No cover letters found for user_id: {'1'}")
            raise HTTPException(
                status_code=404, detail="Cover letters not found for the user"
            )

        # end_time = time.time()
        # print(f"Total execution time: {end_time - start_time:.4f} seconds")

        return cover_letters

    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


# Get cover letter by id
@router.get("/{id}", response_model=schemas.CoverLetterOut)
async def get_cover_letter(id: int, db: Session = Depends(database.get_db)):
    # start_time = time.time()
    # print("Start processing request")

    # try:
    # query_start_time = time.time()
    user_cover_letter = (
        db.query(models.Coverletter)
        .filter(models.Coverletter.user_id == "1")
        .filter(models.Coverletter.id == id)
        .first()
    )
    # for cover in user_cover_letter:
    # print(cover.title, cover.id, cover.user_id, cover.text)
    # query_end_time = time.time()
    # print(f"Query execution time: {query_end_time - query_start_time:.4f} seconds")

    if not user_cover_letter:
        print(f"No cover letter found for user_id: {'1'}")
        raise HTTPException(
            status_code=404, detail="Cover letter not found for the user"
        )
    # print(user_cover_letter.id, user_cover_letter.title, user_cover_letter.user_id)
    # end_time = time.time()
    # print(f"Total execution time: {end_time - start_time:.4f} seconds")

    # return {"cover_letter": user_cover_letter.text}
    return user_cover_letter

    # except SQLAlchemyError as e:
    #     print(f"SQLAlchemy Error: {e}")
    #     raise HTTPException(status_code=500, detail="Database error")
    # except Exception as e:
    #     print(f"General Error: {e}")
    #     raise HTTPException(status_code=500, detail="An error occurred")

    # def create_preview(text, word_limit=25):
    #     words = text.split()
    #     return " ".join(words[:word_limit])


@router.post("", response_model=schemas.CoverLetterOut)
async def create_cover_letter(
    request: schemas.CoverLetterRequest, db: Session = Depends(database.get_db)
):
    # Query the database for the user's CV text
    user_cv = (
        db.query(models.Cv)
        # .filter(models.Cv.user_id == request.user_id)
        .filter(models.Cv.user_id == "1")
        # qui mettiamo un filtro che sceglie il cv cha ha default == true
        .filter(models.Cv.id == "1")
        # .order_by(desc(models.Cv.created_at))
        .first()
    )
    if not user_cv:
        raise HTTPException(status_code=404, detail="CV not found for the user")

    # Extract the text_pdf (transcribed CV text)
    cv_text = user_cv.text_pdf
    try:
        # Generate the prompt
        cover_letter_text = await generate_cover_letter(cv_text, request.jobDescription)

        # Create a new Coverletter instance and save to the database
        new_cover_letter = models.Coverletter(
            text=cover_letter_text,
            title="COVER LETTER APPLE TEST",  # You might want to add a title field in your request schema or generate it differently
            user_id="1",
        )
        db.add(new_cover_letter)
        db.commit()

        return new_cover_letter
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# New endpoint to patch (update) a cover letter by ID
@router.patch("/{id}", response_model=schemas.CoverLetterOut)
async def patch_cover_letter(
    id: int,
    cover_letter_update: schemas.CoverLetterPatch,
    db: Session = Depends(database.get_db),
):
    try:
        cover_letter = (
            db.query(models.Coverletter)
            .filter(models.Coverletter.user_id == "1")
            .filter(models.Coverletter.id == id)
            .first()
        )
        if not cover_letter:
            raise HTTPException(status_code=404, detail="Cover letter not found")

        # Update the fields that are provided in the request
        for key, value in cover_letter_update.model_dump(
            exclude_unset=True, exclude_none=True
        ).items():
            setattr(cover_letter, key, value)

        db.commit()
        db.refresh(cover_letter)
        return cover_letter
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


@router.delete("/{id}", status_code=204)
async def delete_cover_letter(id: int, db: Session = Depends(database.get_db)):
    try:
        cover_letter = (
            db.query(models.Coverletter)
            .filter(models.Coverletter.user_id == "1")
            .filter(models.Coverletter.id == id)
            .first()
        )
        if not cover_letter:
            raise HTTPException(status_code=404, detail="Cover letter not found")

        db.delete(cover_letter)
        db.commit()
        return {"detail": "Cover letter deleted successfully"}
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")
