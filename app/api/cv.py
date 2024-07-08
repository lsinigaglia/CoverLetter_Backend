import logging
import os
from pathlib import Path
from aiohttp import ClientError
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.params import Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc


from app import crud, models, database
from .. import schemas
from ..utils import transcribe_file
from ..config import test_user_id
from ..config import s3_client
from ..config import s3_bucket_name

extracted_text_TEST = """Alexandre Fiaschi  \nBusiness Innovation  \nAiming to revolutionize businesses through the use of innovation and the understanding of our new hyper-evolving environment.\n\nalexandrefiaschi10@gmail.com  \n+39 3939848203  \nRome, Italy  \nlinkedin.com/in/alexandrefiaschi\n\nWORK EXPERIENCE\n------------------------\n\n**Business Analyst / BI  \nSolution 2 Enterprises**  \n06/2021 - Present    \nRome, Italy (Remote)  \nDeveloped a range of Business digital solutions for clients with a focus on Data Management, Consulting Services, and Software Development.\n\n**Achievements/Tasks**  \n* Developed Python script to interact with SQL DB, API's and ETL  \n* PreSales: Understanding clients need for infrastructural IT improvement with use of Elastic Stack  \n* Creation of basic report in Power BI and understanding of KPI about the business  \n* Analysis of IT Operation Management tool market and solutions like Elastic, Confluent (Kafka), Splunk\n\n**Intern - Junior Blockchain Consultant  \nSistemi Informativi / IBM**  \n11/2020 - 05/2021  \nRome, Italy  \n\n**Role/Tasks**  \n* Inside IBM's Business Unit, GBS Blockchain Practice, helping clients to innovate and transform their industries through the use of blockchain solutions  \n* Blockchain Business case histories  \n* Business feasibility scenarios and proof of concept in the Public Administration, Education, Aviation industry\n\n**Intern - Business Innovation (Curricular Internship)  \nHoppipolla / Co-Hive**  \n05/2018 - 09/2018  \nRome, Italy \n\n**Role/Tasks**  \n* Improve business long-term Vision: understanding how the current business model can fit in new diversification opportunities  \n* Business trip (Wien Pioneers Event 2018) to search for investors and find business partners  \n* Competitors and market analysis\n\n**Sail Instructor / Sea Responsible  \nPugnochiuso Resort / Jolly Animation**  \n06/2014 - 09/2014  \nVieste, Italy  \n\n**Achievements/Tasks**  \n* Sailing school and resort nautical center management and maintenance  \n* Private and personalized sailing courses\n\nTECHNICAL SKILLS\n------------------------\n\n**Data**\n* Excel analysis & visualization - Advanced  \n* SQL querying - Basic\n\n**Programming**\n* Python - Mid / C - Basic\n\n**Visualisation Tool**\n* Power BI - Basic\n\n**Writing & Presentation**\n* Office & Power Point - Advanced\n\nSOFT SKILLS\n------------------------\n\n* Critical & Creative Thinking  \n* Curiosity  \n* Long-term business vision / Future Focused  \n* Data Analysis  \n* Good Communicator  \n* Adaptability / Flexibility  \n* Ideas Generator  \n* Problem-Solving  \n* Leadership  \n* Team Work\n\nCERTIFICATES\n------------------------\n\n**IBM Data Analyst (03/2021 - 04/2021)**  \nData analysis with Excel and Dashboard with Cognos Analytics\n\n**HarvardX - CS50 Introduction to Computer Science (02/2021 - Present)**\n\n**Start2Impact - Blockchain Dev (07/2021 - Present)**\n\nEVENTS\n------------------------\n\n**Pioneers - Wein, Austria**  \n2018\n\n**Blockchain Week - Rome, Italy**  \n2018\n\nPERSONAL PROJECTS\n------------------------\n\n**Future Capytal (01/2019 - Present)**  \n* Digital assets private investment fund  \n* Crypto projects analysis  \n* R&D Crypto assets projects\n\nINTERESTS\n------------------------\n\n* Aerospace  \n* Technology  \n* Investment  \n* Music  \n* Disruptive Innovations  \n* Sci-Fi"""

router = APIRouter(prefix="/cvs", tags=["CV"])



# Get list of cvs
@router.get("", response_model=List[schemas.CvOut])
async def get_cv(
    # user_id: int,
    db: Session = Depends(database.get_db),
):
    # Query the database for the user's CV
    user_cvs = (
        db.query(models.Cv)
        .filter(models.Cv.user_id == test_user_id)
        .order_by(desc(models.Cv.created_at))
        .all()
    )

    # if not user_cvs:
    #     raise HTTPException(status_code=404, detail="CVs not found for the user")

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
        .filter(models.Cv.user_id == test_user_id)
        .filter(models.Cv.id == id)
        .first()
    )
    if not user_cv:
        raise HTTPException(status_code=404, detail="CV not found for the user")

    return user_cv


# Upload CV
@router.post("", response_model=schemas.CvOut)
async def upload_and_transcript(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    default_cv: Optional[bool] = Query(False),
):

    user = db.query(models.User).filter(models.User.id == test_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    #file_location = Path("uploaded_cvs") / file.filename

    extracted_text = await transcribe_file(file)
    #extracted_text = extracted_text_TEST  # FOR TESTING

    # Remove .pdf extension from filename
    filename = file.filename
    # Ensure the extension is .pdf before removing it
    if filename.lower().endswith(".pdf"):
        filename_without_extension_for_title = filename[:-4]
    else:
        filename_without_extension_for_title = filename
    
    
    # Upload the PDF to S3
    
    s3_key = f"uploaded_pdfs/{filename}"
    try:
        s3_client.upload_fileobj(file.file, s3_bucket_name, s3_key)
    except ClientError as e:
        # Log the error or include more detailed error information in the response
        logging.error(e)
        raise HTTPException(status_code=500, detail=f"Failed to upload file to S3: {str(e)}")

    #URL of the bucket.     
    s3_url = f"https://{s3_bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_key}"
    
    cv_data = schemas.CVCreate(
        title=filename_without_extension_for_title,
        user_id=test_user_id,
        pdf_path=s3_url,
        text_pdf=extracted_text,
        default_cv=default_cv,
    )

    # Se default_cv è impostato su True, imposta default_cv di tutti gli altri CV su False.
    if cv_data.default_cv:
        db.query(models.Cv).filter(models.Cv.user_id == test_user_id).update(
            {models.Cv.default_cv: False}
        )

    # db_cv = crud.create_cv(db=db, cv=cv_data)
    db_cv = models.Cv(**cv_data.model_dump())
    db.add(db_cv)
    db.commit()
    db.refresh(db_cv)
    return db_cv


# Patch cv
@router.patch("/{id}", response_model=schemas.CvOut)
async def patch_cv(
    id: int,
    cv_update: schemas.CvPatch,
    db: Session = Depends(database.get_db),
):
    try:
        cv = (
            db.query(models.Cv)
            .filter(models.Cv.user_id == test_user_id)
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

        # Se default_cv è impostato su True, imposta default_cv di tutti gli altri CV su False.
        if cv_update.default_cv:
            db.query(models.Cv).filter(
                models.Cv.user_id == test_user_id, models.Cv.id != id
            ).update({models.Cv.default_cv: False})

        db.commit()
        db.refresh(cv)
        return cv
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


# Delete cv
@router.delete("/{id}", status_code=204)
async def delete_cv(id: int, db: Session = Depends(database.get_db)):
    try:
        cv = (
            db.query(models.Cv)
            .filter(models.Cv.user_id == test_user_id)
            .filter(models.Cv.id == id)
            .first()
        )
        if not cv:
            raise HTTPException(status_code=404, detail="Cv not found")

        # Check if the cv to be deleted is the default one
        was_default = cv.default_cv

        # Delete the cover letter
        db.delete(cv)
        db.commit()

        # se era default, imposta l'ultimo cv uplodato come true
        if was_default:
            # Get the most recently created cover letter
            most_recent_cv = (
                db.query(models.Cv)
                .filter(models.Cv.user_id == test_user_id)
                .order_by(models.Cv.created_at.desc())
                .first()
            )

            if most_recent_cv:
                most_recent_cv.default_cv = True
                db.commit()

        # return {"detail": "CV deleted successfully"}
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")
