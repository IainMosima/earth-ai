from fastapi import UploadFile
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    ground_photo: Optional[UploadFile] = None
    aerial_photo: Optional[UploadFile] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    
    class Config:
        arbitrary_types_allowed = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None
    ground_photo: Optional[str] = None
    aerial_photo: Optional[str] = None

class UserSchema(UserBase):
    id: int
    avatar_url: Optional[str] = None
    ground_photo: Optional[str] = None
    aerial_photo: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
