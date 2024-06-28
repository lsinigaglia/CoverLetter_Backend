from fastapi import APIRouter, Depends, HTTPException

from app import models, database
from sqlalchemy.orm import Session
from .. import schemas
from typing import List
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy import desc

router = APIRouter(prefix="/cvs", tags=["CV"])


# get list of cvs
@router.get("", response_model=List[schemas.CvOut])
async def get_cv(
    # user_id: int,
    db: Session = Depends(database.get_db),
):
    # Query the database for the user's CV
    user_cvs = (
        db.query(models.Cv)
        .filter(models.Cv.user_id == "1")
        .order_by(desc(models.Cv.created_at))
        # .first()
        .all()
    )
    if not user_cvs:
        raise HTTPException(status_code=404, detail="CVs not found for the user")

    # return {"cv_text": user_cv.text_pdf}
    return user_cvs


# Get cv by id
@router.get("/{id}")
async def get_cv(
    id: int,
    db: Session = Depends(database.get_db),
):
    # Query the database for the user's CV
    user_cv = (
        db.query(models.Cv)
        .filter(models.Cv.user_id == "1")
        .filter(models.Cv.id == id)
        # .order_by(desc(models.Cv.created_at))
        .first()
    )
    if not user_cv:
        raise HTTPException(status_code=404, detail="CV not found for the user")

    return user_cv
    # return {"cv_text": user_cv.text_pdf}


@router.patch("/{id}", response_model=schemas.CvOut)
async def patch_cv(
    id: int,
    cv_update: schemas.CvPatch,
    db: Session = Depends(database.get_db),
):
    try:
        cv = (
            db.query(models.Cv)
            .filter(models.Cv.user_id == "1")
            .filter(models.Cv.id == id)
            .first()
        )
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found")

        # Update tutti i campi della richiesta
        for key, value in cv_update.model_dump(
            exclude_unset=True, exclude_none=True
        ).items():
            setattr(cv, key, value)

        # # Se default_cv è impostato su True, imposta default_cv di tutti gli altri CV su False.
        # if cv_update.default_cv:
        #     db.query(models.Cv).filter(
        #         models.Cv.user_id == "1", models.Cv.id != id
        #     ).update({models.Cv.default_cv: False})

        db.commit()
        db.refresh(cv)
        return cv
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


@router.delete("/{id}", status_code=204)
async def delete_cv(id: int, db: Session = Depends(database.get_db)):
    try:
        cv = (
            db.query(models.Cv)
            .filter(models.Cv.user_id == "1")
            .filter(models.Cv.id == id)
            .first()
        )
        if not cv:
            raise HTTPException(status_code=404, detail="Cv not found")

        # Check if the cover letter to be deleted is the default one
        # was_default = cover_letter.default_cv

        # Delete the cover letter
        db.delete(cv)
        db.commit()

        # se era default
        # if was_default:
        #     # Get the most recently created cover letter
        #     most_recent_cover_letter = (
        #         db.query(models.Cv)
        #         .filter(models.Cv.user_id == "1")
        #         .order_by(models.Cv.created_at.desc())
        #         .first()
        #     )

        #     if most_recent_cover_letter:
        #         most_recent_cover_letter.default_cv = True
        #         db.commit()

        # return {"detail": "Cover letter deleted successfully"}
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")
