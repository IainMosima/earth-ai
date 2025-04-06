from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, validator
from bson import ObjectId


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
class UserBase(BaseModel):
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
    is_active: bool = True

    class Config:
        populate_by_name = True


# User model for response (with id)
class UserModel(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "_id": "62d7e1eb3c66fe0f0a000001",
                "email": "user@example.com",
                "username": "example_user",
                "ground_photo": "https://storage.example.com/photos/ground123.jpg",
                "aerial_photo": "https://storage.example.com/photos/aerial123.jpg",
                "avatar_url": "https://storage.example.com/avatars/user123.jpg",
                "carbon_score": 78.5,
                "potential_earnings": "$250-300",
                "interested_companies": 3,
                "verification_status": "pending",
                "notification_preferences": {
                    "email": True,
                    "push": False
                },
                "carbon_journey": {
                    "milestones": ["started", "submitted_photos"],
                    "next_step": "verification"
                },
                "is_verified": False,
                "is_active": True,
                "created_at": "2023-04-01T12:00:00.000Z",
                "updated_at": "2023-04-02T14:30:00.000Z"
            }
        }




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
