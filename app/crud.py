from sqlalchemy.orm import Session
from .models import User
from . import models, schemas

def get_or_create_user(db: Session, google_id: str, email: str, name: str, profile_picture: str = None):
    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        user = User(google_id=google_id, email=email, name=name, profile_picture=profile_picture)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_cv(db: Session, cv: schemas.CVCreate):
    db_cv = models.Cv(**cv.model_dump())
    db.add(db_cv)
    db.commit()
    db.refresh(db_cv)
    return db_cv