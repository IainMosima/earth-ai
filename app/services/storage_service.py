import boto3
import os
from dotenv import load_dotenv
from botocore.client import Config

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
        
    async def generate_signed_urls(self, user_id: str) -> dict:
        """
        Generates signed URLs for ground and aerial photo uploads
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Dictionary containing the signed URLs
        """
        print(f"Generating signed URLs for user {user_id}")
        # Common parameters
        expires_in = 3600 * 2  # URL expires in 1 hour
        
        # Generate URL for ground photo
        ground_photo_key = f"users/{user_id}/ground_photo"
        ground_photo_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': ground_photo_key,
                'ContentType': 'image/*'
            },
            ExpiresIn=expires_in
        )
        
        # Generate URL for aerial photo
        aerial_photo_key = f"users/{user_id}/aerial_photo"
        aerial_photo_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': aerial_photo_key,
                'ContentType': 'image/*'
            },
            ExpiresIn=expires_in
        )
        
        return {
            'ground_photo_url': ground_photo_url,
            'ground_photo_key': ground_photo_key,
            'aerial_photo_url': aerial_photo_url,
            'aerial_photo_key': aerial_photo_key
        }

storage_service = StorageService()
