# backend/utils/s3_utils.py
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import uuid
import os
from fastapi import HTTPException
from backend.core.config import settings
from typing import Optional


# Initialize S3 client based on settings
s3_client = None
s3_available = False

if settings.AWS_REGION and settings.S3_BUCKET_NAME:
    try:
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            print(f"Initializing S3 client for region {settings.AWS_REGION} using credentials from settings.")
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        else:
            print(f"Initializing S3 client for region {settings.AWS_REGION} using default credential chain (IAM Role recommended).")
            s3_client = boto3.client('s3', region_name=settings.AWS_REGION)

        # Light check: Verify client object was created
        if s3_client:
             print("S3 client initialized.")
             s3_available = True # Assume available if client created
        else:
             print("S3 client initialization failed silently.")


    except (NoCredentialsError, PartialCredentialsError):
        print("Error: AWS credentials not found or incomplete in settings or default chain. S3 uploads unavailable.")
    except ClientError as e:
        print(f"AWS ClientError during S3 client initialization: {e}. S3 uploads unavailable.")
    except Exception as e:
        print(f"An unexpected error occurred during S3 client initialization: {e}. S3 uploads unavailable.")

else:
    print("S3 Region and/or Bucket Name not configured in settings. S3 uploads unavailable.")


def upload_file_to_s3(file_content: bytes, original_filename: str, content_type: str) -> Optional[str]:
    """
    Uploads file content bytes to S3 and returns the S3 object key if successful, else None.
    """
    if not s3_available or not s3_client:
        print("Skipping S3 upload: S3 client not available or not configured.")
        return None

    # Generate a unique filename using UUID and retain original extension
    file_extension = os.path.splitext(original_filename)[1].lower() # Ensure consistent extension case
    unique_key = f"uploads/{uuid.uuid4()}{file_extension}" # Simple prefix

    print(f"Attempting to upload '{original_filename}' to S3 bucket '{settings.S3_BUCKET_NAME}' with key '{unique_key}'")

    try:
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=unique_key,
            Body=file_content,
            ContentType=content_type or 'application/octet-stream'
        )
        print(f"Successfully uploaded to S3 with key: {unique_key}")
        return unique_key

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        print(f"AWS ClientError uploading to S3: {error_code} - {error_message}")
        #Log the error and return None to indicate failure
        return None
    except Exception as e:
        print(f"An unexpected error occurred during S3 upload: {e}")
        import traceback
        traceback.print_exc()
        return None