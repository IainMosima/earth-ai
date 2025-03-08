from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, MetaData
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base

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
    
    

class UserDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    ground_photo_url: Optional[str] = None
    aerial_photo_url: Optional[str] = None
    registration_complete: bool = False
    
class UserResponseCreation(BaseModel):
    id: int
    email: str
    username: str
    upload_urls: Optional[dict] = []
    avatar_url: Optional[str] = None
    carbon_score: float = 0
    potential_earnings: Optional[str] = None
    interested_companies: int = 0
    verification_status: str = "Pending"
    notification_preferences: dict = {}
    carbon_journey: Optional[dict] = None
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

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
    updated_at: datetime
