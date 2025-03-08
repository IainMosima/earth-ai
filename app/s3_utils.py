import os
import boto3
import uuid
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
from dotenv import load_dotenv
import logging

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

async def validate_image(file: UploadFile):
    # Validate file content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types are: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # Read file content to validate size
    content = await file.read()
    await file.seek(0)  # Reset file pointer after reading
    
    # Validate file size
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed ({MAX_IMAGE_SIZE/1024/1024}MB)"
        )

async def upload_file_to_s3(file: UploadFile, folder: str = "uploads"):
    """
    Upload a file to S3 bucket
    Returns the S3 object key/path
    """
    # First, validate the file
    await validate_image(file)
    
    # Generate a unique filename to prevent overwrites
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Construct the S3 object key (path)
    object_key = f"{folder}/{unique_filename}"
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=object_key,
            Body=file_content,
            ContentType=file.content_type
        )
        
        # Generate the URL for the uploaded file
        url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_key}"
        
        return {
            "key": object_key,
            "url": url
        }
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 upload error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def delete_file_from_s3(object_key: str):
    """
    Delete a file from S3 bucket by its object key
    """
    if not object_key:
        return
        
    try:
        s3_client.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=object_key
        )
        return True
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 delete error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
