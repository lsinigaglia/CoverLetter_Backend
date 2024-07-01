# app/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True)
    name = Column(String)
    # first_name = Column(String)
    # last_name = Column(String)
    email = Column(String, unique=True, index=True)
    profile_picture = Column(
        String
    )  # Store the URL to the user's profile picture if needed
    # email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    cover_letter_tokens = Column(Integer, nullable=False)
    cvs = relationship("Cv", back_populates="user")
    coverletters = relationship("Coverletter", back_populates="user")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Cv(Base):
    __tablename__ = "cvs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    pdf_path = Column(String, nullable=False)
    text_pdf = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    default_cv = Column(Boolean, default=False)
    user = relationship("User", back_populates="cvs")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Coverletter(Base):
    __tablename__ = "coverletters"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)  # it will be a .docx file i suppose
    title = Column(String)
    poster = Column(String)
    cv_id = Column(Integer, ForeignKey("cvs.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="coverletters")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
