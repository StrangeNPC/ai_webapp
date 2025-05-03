# backend/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.api.v1.api import api_router # Keep this import
from backend.core.config import settings
from backend.db.database import engine, Base

# --- Optional: Create DB Tables ---
def create_db_tables():
    if engine:
        try:
            print("Attempting to create database tables if they don't exist...")
            Base.metadata.create_all(bind=engine)
            print("Database tables check/creation complete.")
        except Exception as e:
            print(f"Error during initial table creation (DB connection issue? Permissions?): {e}")
    else:
        print("Database engine not available. Skipping table creation.")

create_db_tables()

# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    # Update openapi_url if you remove the prefix, or keep it if you want docs at /api/v1/openapi.json
    # If you want docs at /openapi.json, remove the prefix here too. Let's keep it for now.
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include API Router ---
# REMOVED the prefix=settings.API_V1_STR
app.include_router(api_router)

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    """ Basic API health check / welcome message """
    return {"message": f"Welcome to the {settings.PROJECT_NAME}!"}


# --- Global Exception Handlers ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    print(f"HTTP Exception Caught: Status={exc.status_code}, Detail={exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Catch-all for unexpected errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    print(f"FATAL: Unexpected Server Error Caught: {exc}")
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please contact support or check server logs."},
    )

# --- Local Running Block ---
if __name__ == "__main__":
    import uvicorn
    print("Starting Uvicorn server locally on http://0.0.0.0:8000")
    # Make sure the reload points to the correct app instance if running locally
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)