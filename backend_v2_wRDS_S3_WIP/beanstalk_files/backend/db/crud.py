# backend/db/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def create_analysis_record(db: Session, record: schemas.AnalysisRecordCreate) -> models.AnalysisRecord:
    """
    Creates a new analysis record in the database.
    """
    db_record = models.AnalysisRecord(
        original_filename=record.original_filename,
        s3_object_key=record.s3_object_key,
        analysis_summary=record.analysis_summary,
        analysis_nationalities=record.analysis_nationalities,
        analysis_organizations=record.analysis_organizations,
        analysis_people=record.analysis_people
    )
    db.add(db_record)
    try:
        db.commit()
        db.refresh(db_record)
        print(f"Successfully saved analysis record with ID: {db_record.id}")
        return db_record
    except Exception as e:
        db.rollback()
        print(f"CRITICAL: Error committing analysis record to database: {e}")
        return None # Indicate failure
