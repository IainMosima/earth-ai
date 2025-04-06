from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.requests.S3 import SignedUrlsResponse
from app.utils.Enums import VerificationStatusEnum


# Pydantic models for response
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    avatar_url: Optional[str]
    ground_photo_content_type: Optional[str] = "image/jpeg"
    aerial_photo_content_type: Optional[str] = "image/tiff"


class UserResponse(UserBase):
    id: int
    ground_photo: Optional[str] = None
    aerial_photo: Optional[str] = None
    is_verified: bool = False
    created_at: Optional[datetime] = None

class UserResponseCreation(BaseModel):
    id: str
    email: str
    name: str
    created_at: str
    upload_urls: SignedUrlsResponse

# User update model (all fields optional)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    ground_photo: Optional[str] = None
    aerial_photo: Optional[str] = None
    avatar_url: Optional[str] = None
    carbon_score: Optional[float] = None
    potential_earnings: Optional[str] = None
    interested_companies: Optional[int] = None
    verification_status: Optional[VerificationStatusEnum] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    carbon_journey: Optional[Dict[str, Any]] = None
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None
    verification_thread_id: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)