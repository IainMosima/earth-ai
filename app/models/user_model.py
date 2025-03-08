from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Pydantic models for response
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserResponse(UserBase):
    id: int
    registration_complete: bool = False
    ground_photo: Optional[str] = None
    aerial_photo: Optional[str] = None
    created_at: Optional[datetime] = None


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Add this line to handle duplicate definitions

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    ground_photo = Column(String, nullable=True)
    aerial_photo = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    carbon_score = Column(Float, default=0)
    potential_earnings = Column(String, nullable=True)
    interested_companies = Column(Integer, default=0)
    verification_status = Column(Enum("Pending", "Rejected", "Accepted", name="verification_status_enum"), default="Pending")
    notification_preferences = Column(JSON, default={})
    carbon_journey = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with companies if needed
    # companies = relationship("Company", back_populates="owner")
