# backend/core/file_processor.py
import io
import docx # python-docx
from fastapi import HTTPException, UploadFile

async def read_uploaded_file(file: UploadFile) -> str:
    """Reads content from UploadFile (txt or docx)."""
    filename = file.filename
    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail=f"Uploaded file '{filename}' appears to be empty.")

    if filename.lower().endswith(".txt"):
        try:
            # Try UTF-8 first
            return contents.decode("utf-8")
        except UnicodeDecodeError:
            print(f"Warning: Decoding {filename} as UTF-8 failed, trying Latin-1.")
            try:
                # Fallback to Latin-1
                return contents.decode("latin-1")
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not decode .txt file '{filename}'. Ensure it's UTF-8 or Latin-1 encoded. Error: {e}"
                )
    elif filename.lower().endswith(".docx"):
        try:
            doc_stream = io.BytesIO(contents)
            doc = docx.Document(doc_stream)
            full_text = [para.text for para in doc.paragraphs]
            return '\n'.join(full_text)
        except Exception as e:
            # Catch potential errors from python-docx (e.g., bad zip file)
            print(f"Error reading docx file '{filename}': {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Could not parse the .docx file '{filename}'. It might be corrupted or not a valid Word document. Error: {e}"
            )
    else:
        # This case might be redundant if validated earlier, but good defensively
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type for '{filename}'. Only .txt and .docx are supported."
        )