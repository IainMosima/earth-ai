from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, MetaData
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel

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
    pass

class UserDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    ground_photo_url: Optional[str] = None
    aerial_photo_url: Optional[str] = None
    registration_complete: bool = False
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "_id": "60d21b4967d0d1992e610c85",
                "email": "user@example.com",
                "ground_photo_url": None,
                "aerial_photo_url": None,
                "registration_complete": False
            }
        }

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    registration_complete: bool

class UserCreate(BaseModel):
    email: EmailStr
    username: str

# class User(Base):
#     __tablename__ = "users"
    
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     username = Column(String, unique=True, index=True)
#     ground_photo_url = Column(String, nullable=True)
#     aerial_photo_url = Column(String, nullable=True)
#     registration_complete = Column(Boolean, default=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
