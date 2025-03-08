import boto3
import os
from dotenv import load_dotenv
from botocore.client import Config
from datetime import datetime, timezone
import json
import base64

from app.models.S3 import S3SignedURLs

load_dotenv()

class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')

    async def generate_signed_urls(self, user_id: int, webhook_url: str = None) -> S3SignedURLs:
        """
        Generates signed URLs for ground and aerial photo uploads with webhook capabilities.
        
        Args:
            user_id (int): The ID of the user
            webhook_url (str, optional): URL to be called after successful upload
            
        Returns:
            dict: Dictionary containing signed URLs and metadata.
        """
   
        expires_in = 3600 * 24  # 24 hours expiration
        
        # Create metadata that will be available to webhook
        timestamp = datetime.now(timezone.utc).isoformat()
        metadata = {
            'user_id': str(user_id),
            'timestamp': timestamp,
            'webhook_url': webhook_url if webhook_url else '',
            'process_after_upload': 'true'
        }
        
        # Encode metadata for URL safety if needed
        encoded_metadata = base64.urlsafe_b64encode(json.dumps(metadata).encode()).decode()

        # Generate URLs
        ground_photo_key = f"users/{user_id}/ground_photo"
        ground_photo_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': ground_photo_key,
                'ContentType': 'image/*',
                'ACL': 'public-read',
                'Metadata': {
                    'user-id': str(user_id),
                    'timestamp': timestamp,
                    'webhook-url': webhook_url if webhook_url else '',
                    'upload-type': 'ground_photo',
                    'encoded-metadata': encoded_metadata
                }
            },
            ExpiresIn=expires_in
        )

        aerial_photo_key = f"users/{user_id}/aerial_photo"
        aerial_photo_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': aerial_photo_key,
                'ContentType': 'image/*',
                'ACL': 'public-read',
                'Metadata': {
                    'user-id': str(user_id),
                    'timestamp': timestamp,
                    'webhook-url': webhook_url if webhook_url else '',
                    'upload-type': 'aerial_photo',
                    'encoded-metadata': encoded_metadata
                }
            },
            ExpiresIn=expires_in
        )
        
        # Return as a dictionary with user_id and metadata included
        return S3SignedURLs(
            ground_photo_signed=ground_photo_url,
            aerial_photo_signed=aerial_photo_url,
            ground_photo_url=f"https://{self.bucket_name}.s3.amazonaws.com/{ground_photo_key}",
            ground_photo_key=ground_photo_key,
            aerial_photo_url=f"https://{self.bucket_name}.s3.amazonaws.com/{aerial_photo_key}",
            aerial_photo_key=aerial_photo_key,
            user_id=user_id,
            metadata=metadata
        )

# Example usage:
storage_service = StorageService()