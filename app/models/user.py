from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr


# Custom ObjectId field for MongoDB
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str) and not isinstance(v, ObjectId):
            raise ValueError("Not a valid ObjectId")
        return str(v)


# Enum for verification status
class VerificationStatusEnum(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    IN_REVIEW = "in_review"


# Base User model for shared attributes
class UserBaseDB(BaseModel):
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
    carbon_journey: Optional[Dict[str, Any]] = None,
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_verified: bool = False
    verification_thread_id: Optional[str] = None
    is_active: bool = True


# User model for response (with id)
class UserModel(UserBaseDB):
    id: PyObjectId = Field(default_factory=PyObjectId)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None



# Function to help convert Pydantic models to MongoDB documents
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"],
        "ground_photo": user.get("ground_photo"),
        "aerial_photo": user.get("aerial_photo"),
        "avatar_url": user.get("avatar_url"),
        "carbon_score": user.get("carbon_score", 0),
        "potential_earnings": user.get("potential_earnings"),
        "interested_companies": user.get("interested_companies", 0),
        "verification_status": user.get("verification_status", "pending"),
        "notification_preferences": user.get("notification_preferences", {}),
        "carbon_journey": user.get("carbon_journey"),
        "is_verified": user.get("is_verified", False),
        "is_active": user.get("is_active", True),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at")
    }
