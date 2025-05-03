# backend/api/v1/endpoints/analysis.py
import os # Ensure this is present
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, Annotated

from backend.db import schemas, crud
from backend.db.database import get_db, IS_DB_CONNECTED
from backend.core import file_processor, analysis_service
from backend.utils import s3_utils
from backend.core.config import settings

router = APIRouter()

# Allowed file types
ALLOWED_CONTENT_TYPES = ["text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
ALLOWED_EXTENSIONS = [".txt", ".docx"]

# Ensure the path here is "/analyze" to match the test script endpoint
@router.post("/analyze", response_model=schemas.AnalysisResponse)
async def analyze_article(
    # Use Annotated for richer validation/metadata (FastAPI 0.95+)
    text_content: Annotated[Optional[str], Form()] = None,
    file_upload: Annotated[Optional[UploadFile], File()] = None,
    db: Session = Depends(get_db)
):
    """
    Analyzes news article text (either provided directly via 'text_content' form field
    or via 'file_upload' field for .txt or .docx files)
    to generate a summary and extract nationalities, organizations, and people.

    - If a file is uploaded, it's stored in S3 (if configured).
    - Analysis results are saved to the database (if configured).
    """
    article_text: str = ""
    original_filename: Optional[str] = None
    s3_key: Optional[str] = None
    file_bytes: Optional[bytes] = None # Store file content for S3 if needed

    # --- Input Validation and Content Extraction ---
    if file_upload:
        # Basic validation
        if not file_upload.filename:
            raise HTTPException(status_code=400, detail="Uploaded file is missing a filename.")

        # Check content type first
        content_type_valid = file_upload.content_type in ALLOWED_CONTENT_TYPES
        # Check extension as fallback or primary if content type is generic
        file_ext = os.path.splitext(file_upload.filename)[1].lower()
        extension_valid = file_ext in ALLOWED_EXTENSIONS

        if not content_type_valid and not extension_valid:
             raise HTTPException(status_code=400, detail=f"Invalid file content type '{file_upload.content_type}' or extension '{file_ext}'. Allowed types: .txt, .docx")

        original_filename = file_upload.filename
        print(f"Processing uploaded file: {original_filename}")

        try:
            # Read content using the file processor
            # Need the bytes for S3 later
            file_bytes = await file_upload.read() # Read once
            await file_upload.seek(0) # Reset cursor in case processor needs to read again
            # Note: Refactor file_processor.read_uploaded_file to accept bytes?
            # For now, re-reading via UploadFile object:
            article_text = await file_processor.read_uploaded_file(file_upload)

        except HTTPException as e:
            # Re-raise file processing errors (like bad format, decode errors)
            raise e
        except Exception as e:
            print(f"Unexpected error reading file {original_filename}: {e}")
            raise HTTPException(status_code=500, detail="Server error while reading the uploaded file.")

        # --- S3 Upload Attempt ---
        if s3_utils.s3_available and file_bytes:
             # Determine content type for S3, prioritize official type if valid
             s3_content_type = file_upload.content_type if content_type_valid else 'application/octet-stream'
             if not content_type_valid and extension_valid: # Use extension to guess if needed
                 if file_ext == '.txt': s3_content_type = 'text/plain'
                 elif file_ext == '.docx': s3_content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

             s3_key = s3_utils.upload_file_to_s3(
                 file_content=file_bytes,
                 original_filename=original_filename,
                 content_type=s3_content_type
             )
             if s3_key:
                 print(f"File successfully uploaded to S3 with key: {s3_key}")
             else:
                 print("S3 upload failed or was skipped.")
                 # Decide if this failure should block the request or just be logged. Logging for now.

    elif text_content:
        print("Processing text content input.")
        article_text = text_content
    else:
        raise HTTPException(status_code=400, detail="No input provided. Please provide 'text_content' or upload a 'file_upload'.")

    # --- Final Content Checks ---
    if not article_text or not article_text.strip():
        input_source = f"file '{original_filename}'" if original_filename else "text_content"
        raise HTTPException(status_code=400, detail=f"Input {input_source} is effectively empty.")

    if len(article_text) > settings.MAX_TEXT_LENGTH:
         raise HTTPException(status_code=413, detail=f"Input text exceeds maximum length of {settings.MAX_TEXT_LENGTH} characters.")

    # --- Perform Analysis ---
    try:
        print(f"Starting analysis for input length: {len(article_text)}")
        analysis_data = await analysis_service.perform_analysis(article_text)
    except HTTPException as e:
        # Handle specific errors raised by the analysis service (e.g., OpenAI errors, length limits)
        raise e
    except Exception as e:
        print(f"Unexpected error during analysis service call: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An unexpected error occurred during analysis.")


    # --- Database Saving ---
    db_record_id: Optional[int] = None
    if IS_DB_CONNECTED and db:
        record_to_create = schemas.AnalysisRecordCreate(
            original_filename=original_filename,
            s3_object_key=s3_key,
            analysis_summary=analysis_data.get('summary'),
            analysis_nationalities=analysis_data.get('nationalities'),
            analysis_organizations=analysis_data.get('organizations'),
            analysis_people=analysis_data.get('people')
        )
        # crud.create_analysis_record handles commit/rollback internally
        db_record = crud.create_analysis_record(db=db, record=record_to_create)
        if db_record:
            db_record_id = db_record.id # Get the ID if save was successful
        else:
            print("Warning: Failed to save analysis results to database.")
            # Decide if frontend needs to know about DB save failure

    elif IS_DB_CONNECTED and not db:
        # This case means DB is configured, but get_db() failed for this request
        print("Warning: Database session not available for this request. Results not saved.")
    else:
        # DB not configured case - already logged at startup
        pass

    # --- Prepare and Return Response ---
    response = schemas.AnalysisResponse(
        filename=original_filename,
        s3_object_key=s3_key,
        summary=analysis_data.get('summary'),
        nationalities=analysis_data.get('nationalities', []),
        organizations=analysis_data.get('organizations', []),
        people=analysis_data.get('people', [])
        # record_id=db_record_id # Optionally include record ID
    )

    return response