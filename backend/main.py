# backend/main.py
import os
import io
# ADD 'Any' HERE
from typing import Optional, Any
# --- Keep other imports ---
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
# from pydantic import BaseModel # Not strictly needed here
import openai
import docx

# --- Keep load_dotenv() and Configuration ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY not found in environment variables.")
if OPENAI_API_KEY:
     openai.api_key = OPENAI_API_KEY
else:
    print("Warning: OpenAI API Key not configured. API calls will fail.")

# --- Keep FastAPI App Initialization and CORS Middleware ---
app = FastAPI(title="AI News Analyzer API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Keep Helper Functions (get_openai_completion, summarize_text, extract_nationalities, read_docx) ---
# ... (ensure these are still present and correct) ...
def get_openai_completion(prompt_text, model="gpt-3.5-turbo"):
    """Calls the OpenAI Chat Completion API."""
    if not OPENAI_API_KEY:
         raise HTTPException(status_code=500, detail="OpenAI API key not configured on the server.")
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_text}
            ]
        )
        if response.choices and len(response.choices) > 0:
            message_content = response.choices[0].message.content
            if message_content:
                return message_content.strip()
        print("Warning: Could not extract content from OpenAI response structure:", response)
        # Handle cases where the response might be valid but empty or unexpected
        if response.choices and len(response.choices) > 0 and response.choices[0].message is None:
             return "OpenAI returned an empty message."
        return "Error: Could not extract content from OpenAI response."

    except openai.APIError as e:
         print(f"OpenAI API returned an API Error: {e}")
         raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {e}")
        raise HTTPException(status_code=503, detail=f"OpenAI Connection Error: {e}")
    except openai.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
        raise HTTPException(status_code=429, detail=f"OpenAI Rate Limit Exceeded: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during OpenAI call: {e}")
        import traceback
        traceback.print_exc() # Print stack trace for debugging
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

def summarize_text(text):
    """Generates a summary using OpenAI."""
    prompt = f"""
    Please summarize the following news article in 2-4 concise sentences:

    \"\"\"
    {text}
    \"\"\"

    Summary:
    """
    return get_openai_completion(prompt)

def extract_nationalities(text):
    """Extracts nationalities/countries using OpenAI."""
    prompt = f"""
    Analyze the following news article and list all mentioned nationalities, countries, or peoples.
    If a country is mentioned (e.g., France, Japan), list the country name.
    If a nationality or people is mentioned (e.g., French, Japanese, Canadians), list the nationality/people.
    Provide the output as a comma-separated list. If none are found, respond with "None".

    Article:
    \"\"\"
    {text}
    \"\"\"

    Nationalities/Countries mentioned (comma-separated):
    """
    result = get_openai_completion(prompt)
    # Added more robust check for non-error, non-"None" results
    if result and isinstance(result, str) and not result.startswith("Error:") and not result.startswith("OpenAI returned") and result.lower().strip() != "none":
        return [item.strip() for item in result.split(',') if item.strip()]
    else:
        if result and (result.startswith("Error:") or result.startswith("OpenAI returned")):
             print(f"Warning/Error extracting nationalities: {result}") # Log the specific error
        return [] # Return empty list on "None" or error

def read_docx(file_content: bytes) -> str:
    """Reads text content from a .docx file's bytes."""
    try:
        doc_stream = io.BytesIO(file_content)
        doc = docx.Document(doc_stream)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error reading docx file: {e}")
        raise HTTPException(status_code=400, detail=f"Could not read the .docx file. Error: {e}")

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "Welcome to the AI News Analyzer API"}

@app.post("/analyze")
async def analyze_article(
    text_content: Optional[str] = Form(None),
    # CHANGE THIS LINE BACK: Use Optional[UploadFile]
    file_upload: Optional[UploadFile] = File(None)
):
    """
    Analyzes news article text (either provided directly or via file upload)
    to generate a summary and extract nationalities.
    Accepts either 'text_content' (string) or 'file_upload' (.txt or .docx).
    """
    article_text = ""
    filename = None

    # --- Input Validation and Reading ---
    # ADD isinstance check here
    if file_upload: # Check if it's not None first
        # FastAPI should now ensure file_upload IS an UploadFile if provided
        if not file_upload.filename:
            raise HTTPException(status_code=400, detail="Uploaded file is missing a filename.")

        filename = file_upload.filename
        print(f"Received file: {filename}")
        contents = await file_upload.read()
        # Check if file content is empty AFTER reading
        if not contents:
             raise HTTPException(status_code=400, detail=f"Uploaded file '{filename}' appears to be empty.")

        # --- File type processing remains the same ---
        if filename.lower().endswith(".txt"):
            try:
                article_text = contents.decode("utf-8")
            except UnicodeDecodeError:
                try:
                     article_text = contents.decode("latin-1")
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Could not decode .txt file '{filename}'. Ensure it's UTF-8 or Latin-1 encoded. Error: {e}")
        elif filename.lower().endswith(".docx"):
             try:
                article_text = read_docx(contents)
             except HTTPException as e:
                 # Add filename to the error detail if possible
                 e.detail = f"Error processing file '{filename}': {e.detail}"
                 raise e
             except Exception as e:
                print(f"Unexpected error reading .docx '{filename}': {e}")
                raise HTTPException(status_code=500, detail=f"Server error processing .docx file '{filename}': {e}")
        else:
            raise HTTPException(status_code=400, detail=f"Invalid file type for '{filename}'. Please upload a .txt or .docx file.")

    elif text_content:
        print("Received text content.")
        article_text = text_content
    else:
        # This condition is reached if text_content is None/empty AND
        # file_upload was None or not an UploadFile instance (e.g., the empty string '')
        raise HTTPException(status_code=400, detail="No input provided. Please provide text_content or upload a valid file.")

    # Check for empty text *after* potentially reading from file or getting text_content
    if not article_text.strip():
         input_source = f"file '{filename}'" if filename else "text_content"
         raise HTTPException(status_code=400, detail=f"Input {input_source} is empty.")

    MAX_LENGTH = 15000
    if len(article_text) > MAX_LENGTH:
         raise HTTPException(status_code=413,
                             detail=f"Input text is too long ({len(article_text)} > {MAX_LENGTH} chars). Please provide shorter text.")

    # --- Processing ---
    print("Input text length:", len(article_text))
    print("Calling OpenAI for summary...")
    summary = summarize_text(article_text)
    print("Calling OpenAI for nationalities...")
    nationalities = extract_nationalities(article_text)
    print("Analysis complete.")

    # --- Return Response ---
    return {
        "filename": filename, # Will be None if text_content was used
        "summary": summary,
        "nationalities": nationalities
    }


# --- Keep Exception Handlers ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    print(f"An unexpected error occurred: {exc}")
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )


# --- Keep local running block ---
if __name__ == "__main__":
    import uvicorn
    # Ensure reload=True works well by using string format "main:app"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)