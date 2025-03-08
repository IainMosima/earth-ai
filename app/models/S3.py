from pydantic import BaseModel
from typing import Optional, Dict, Any

from datetime import datetime, timezone

from app.utils.Enums import ImageTypeEnum

class S3Callback(BaseModel):
    """
    Model for S3 upload completion callback data
    """
    key: str
    userId: str
    # image_type: Optional[ImageTypeEnum]
    

class SignedUrlsResponse(BaseModel):
    """
    Response model for signed URLs generation
    """
    user_id: int  # Add this missing required field
    ground_photo_url: str
    ground_photo_key: str
    aerial_photo_url: str
    aerial_photo_key: str
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            user_id=data["user_id"],
            ground_photo_url=data["ground_photo_url"],
            ground_photo_key=data["ground_photo_key"],
            aerial_photo_url=data["aerial_photo_url"],
            aerial_photo_key=data["aerial_photo_key"],
            created_at=data["created_at"]
        )

class S3SignedURLs(BaseModel):
    """
    Model for the response from generate_signed_urls function
    """
    ground_photo_signed: str
    aerial_photo_signed: str
    # Add missing attributes that are expected by the consuming code
    ground_photo_url: str
    ground_photo_key: str
    aerial_photo_url: str
    aerial_photo_key: str
    user_id: int
    
    created_at: datetime = datetime.now(timezone.utc)

    @classmethod
    def from_dict(cls, data: dict) -> "S3SignedURLs":
        return cls(**data)


