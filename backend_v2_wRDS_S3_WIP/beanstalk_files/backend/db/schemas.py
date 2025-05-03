from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Base Schemas
class AnalysisRecordBase(BaseModel):
    original_filename: Optional[str] = None
    s3_object_key: Optional[str] = None
    analysis_summary: Optional[str] = None
    analysis_nationalities: Optional[List[str]] = []
    analysis_organizations: Optional[List[str]] = []
    analysis_people: Optional[List[str]] = []

# Schema for creating records in DB
class AnalysisRecordCreate(AnalysisRecordBase):
    pass

# --- Schema for reading records from DB (includes ID, timestamps) ---
class AnalysisRecord(AnalysisRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Pydantic V2 way to allow ORM mode

# --- Schema for the API response from /analyze endpoint ---
# This might differ slightly if you don't return everything from the DB record
class AnalysisResponse(BaseModel):
    filename: Optional[str] = None
    s3_object_key: Optional[str] = None
    summary: Optional[str] = None
    nationalities: List[str] = []
    organizations: List[str] = []
    people: List[str] = []
