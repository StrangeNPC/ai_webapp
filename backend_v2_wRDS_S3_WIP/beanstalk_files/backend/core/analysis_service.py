from typing import Dict, List, Optional
from . import openai_utils
from fastapi import HTTPException
from backend.core.config import settings

async def perform_analysis(text: str) -> dict:
    """
    Performs summary, nationality, and entity extraction on the input text.
    Returns a dictionary containing the analysis results.
    """
    if not text or not text.strip():
         raise ValueError("Input text for analysis cannot be empty.")

    if len(text) > settings.MAX_TEXT_LENGTH:
         # This check should also ideally happen before calling
         raise HTTPException(
             status_code=413,
             detail=f"Input text is too long ({len(text)} chars). Maximum allowed is {settings.MAX_TEXT_LENGTH}."
        )

    analysis_results = {}
    errors = []

    try:
        print("Analysis Service: Generating summary...")
        analysis_results['summary'] =openai_utils.summarize_text(text)
    except Exception as e:
        print(f"Analysis Service Error (Summary): {e}")
        errors.append("Summary generation failed.")
        analysis_results['summary'] = None # Or some error indicator

    try:
        print("Analysis Service: Extracting nationalities...")
        analysis_results['nationalities'] =openai_utils.extract_nationalities(text)
    except Exception as e:
        print(f"Analysis Service Error (Nationalities): {e}")
        errors.append("Nationality extraction failed.")
        analysis_results['nationalities'] = []

    try:
        print("Analysis Service: Extracting entities...")
        entities = openai_utils.extract_entities(text)
        analysis_results['organizations'] = entities.get("organizations", [])
        analysis_results['people'] = entities.get("people", [])
    except Exception as e:
        print(f"Analysis Service Error (Entities): {e}")
        errors.append("Entity extraction failed.")
        analysis_results['organizations'] = []
        analysis_results['people'] = []

    # Optionally include errors in the result if needed
    # analysis_results['errors'] = errors
    if errors:
        print(f"Analysis completed with errors: {errors}")

    print("Analysis Service: Analysis complete.")
    return analysis_results