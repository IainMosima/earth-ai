import os

import boto3
from dotenv import load_dotenv

from app.requests.S3 import SignedUrlsResponse

load_dotenv()


class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')

    async def generate_signed_urls(self, user_id: str, ground_photo_content_type: str = "image/jpeg", aerial_photo_content_type: str = "tiff/jpeg") -> SignedUrlsResponse:
        # Ensure user_id is a string and not None
        user_id = str(user_id)
        valid_images = ["image/jpeg", "image/png", "image/tiff"]

        # Set URL expiration time
        expires_in = 3600 * 12  # expire after 12 hrs

        # Check if bucket name is properly set
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is not set")

        # Generate URL for ground photo
        ground_photo_key = f"ground_photo-{user_id}"
        ground_photo_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': ground_photo_key,
                'ContentType': ground_photo_content_type,
            },
            ExpiresIn=expires_in
        )

        # Generate URL for aerial photo
        aerial_photo_key = f"aerial_photo-{user_id}"
        aerial_photo_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': aerial_photo_key,
                'ContentType': aerial_photo_content_type,
            },
            ExpiresIn=expires_in
        )

        # Return as S3-signed-urls object
        return SignedUrlsResponse(
            ground_photo_signed_url=ground_photo_url,
            aerial_photo_signed_url=aerial_photo_url,
            ground_photo_key=ground_photo_key,
            aerial_photo_key=aerial_photo_key,
        )


# Create a singleton instance
storage_service = StorageService()
