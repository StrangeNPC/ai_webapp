# backend/core/config.py
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    PROJECT_NAME: str = "AI News Analyzer Backend"
    API_V1_STR: str = "/api/v1"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY") 
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # AWS Credentials (Use IAM Role/Instance Profile in production on EB/EC2)
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")   
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY") 
    AWS_REGION: Optional[str] = os.getenv("AWS_REGION") 

    # S3
    S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME") 

    # RDS Database
    DB_TYPE: Optional[str] = os.getenv("DB_TYPE") 
    DB_DRIVER: Optional[str] = os.getenv("DB_DRIVER") 
    DB_USERNAME: Optional[str] = os.getenv("DB_USERNAME") 
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD") 
    DB_HOST: Optional[str] = os.getenv("DB_HOST") 
    DB_PORT: Optional[str] = os.getenv("DB_PORT") 
    DB_NAME: Optional[str] = os.getenv("DB_NAME") 

    # Construct Database URL
    SQLALCHEMY_DATABASE_URL: Optional[str] = None 
    if all([DB_TYPE, DB_DRIVER, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        # Example for PostgreSQL: "postgresql+psycopg2://user:password@host:port/dbname"
        # Example for MySQL: "mysql+mysqlconnector://user:password@host:port/dbname"
        SQLALCHEMY_DATABASE_URL = f"{DB_TYPE}+{DB_DRIVER}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        print(f"Database URL configured: {DB_TYPE}://{DB_USERNAME}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    else:
        print("Warning: Database environment variables not fully configured.")

    # Text Processing Limits
    MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", 20000))


settings = Settings()

# --- Simple Checks ---
if not settings.OPENAI_API_KEY:
    print("CRITICAL: OPENAI_API_KEY not found in environment variables. OpenAI calls will fail.")

if settings.SQLALCHEMY_DATABASE_URL:
     print("Database connection string is configured.")
else:
     print("Database connection string is NOT configured. Results will not be saved to DB.")

# Check S3 essential config
s3_configured = bool(settings.AWS_REGION and settings.S3_BUCKET_NAME)
# Credential check is handled within s3_utils initialization
if s3_configured:
    print("S3 Region and Bucket Name are configured.")
else:
    print("S3 Region and/or Bucket Name are NOT configured. S3 uploads will be skipped.")