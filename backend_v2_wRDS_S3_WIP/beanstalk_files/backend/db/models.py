from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base # Use relative import

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=True, index=True)
    s3_object_key = Column(String(1024), nullable=True, unique=True, index=True) # Added index
    analysis_summary = Column(Text, nullable=True)
    analysis_nationalities = Column(JSON, nullable=True)
    analysis_organizations = Column(JSON, nullable=True)
    analysis_people = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())