from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, MetaData
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base
from app.models.S3 import S3SignedURLs
from typing import Optional, Dict, Any
from enum import Enum

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str) and not isinstance(v, ObjectId):
            raise ValueError("Not a valid ObjectId")
        return str(v)

class UserBase(BaseModel):
    email: EmailStr
    username: str
    
class UserCreate(UserBase):
    avatar_url: Optional[str] = None
    
    
class VerificationStatusEnum(str, Enum):
    PENDING = "Pending"
    VERIFIED = "Verified"
    REJECTED = "Rejected"

class User(BaseModel):
    id: int
    email: EmailStr
    username: str
    ground_photo: Optional[str] = None
    aerial_photo: Optional[str] = None
    avatar_url: Optional[str] = None
    carbon_score: float = 0
    potential_earnings: Optional[str] = None
    interested_companies: int = 0
    verification_status: VerificationStatusEnum = VerificationStatusEnum.PENDING
    notification_preferences: Dict[str, Any] = Field(default_factory=dict)
    carbon_journey: Optional[Dict[str, Any]] = None
    is_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

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

class UserResponseCreation(BaseModel):
    id: int
    email: str
    username: str
    upload_urls: S3SignedURLs
    avatar_url: Optional[str] = None
    carbon_score: float = 0
    potential_earnings: Optional[str] = None
    interested_companies: Optional[int] = 0
    verification_status: str = "Pending"
    notification_preferences: Optional[dict] = {}
    carbon_journey: Optional[dict] = None
    is_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    # upload_config: Optional[dict] = {
    #     "bucket": "qijaniproductsbucket",
    #     "region": "eu-north-1",
    #     "allowed_types": ["image/jpeg", "image/png"]
    # }

class UserResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str
    username: str
    ground_photo: Optional[str] = None
    aerial_photo: Optional[str] = None
    avatar_url: Optional[str] = None
    potential_earnings: Optional[str] = None
    interested_companies: int = 0
    verification_status: str = "Pending"
    notification_preferences: dict = {}
    carbon_journey: Optional[dict] = None
    is_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    upload_config: Optional[dict] = {
        "bucket": "qijaniproductsbucket",
        "region": "eu-north-1",
        "allowed_types": ["image/jpeg", "image/png"]
    }
