# user_repository.py
import logging
from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException, status
from passlib.context import CryptContext
from pydantic import EmailStr

from app.db.database import connect_to_mongo, db
from app.models.user import UserBaseDB, VerificationStatusEnum
from app.requests.user import UserUpdate, UserCreate, UserResponseCreation

# Configure logging
logger = logging.getLogger("user_repository")

# Password handling
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Helper to convert MongoDB ObjectId to string
def serialize_user(user):
    if user:
        user["id"] = str(user.get("_id"))
        user.pop("_id", None)

    return user


async def get_user(user_id: str):
    """Get user by ID"""
    try:
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        return serialize_user(user)
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None


async def get_user_by_email(email: EmailStr):
    """Get user by email"""
    try:
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"email": email})
        return serialize_user(user)
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None


async def get_user_by_username(username: str):
    """Get user by username"""
    try:
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"username": username})
        return serialize_user(user)
    except Exception as e:
        logger.error(f"Error getting user by username: {e}")
        return None


async def get_users(skip: int = 0, limit: int = 100):
    """Get all users with pagination"""
    try:
        users_collection = db.get_collection("users")
        cursor = users_collection.find().skip(skip).limit(limit)
        users = []
        async for user in cursor:
            users.append(serialize_user(user))
        return users
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return []


async def create_user(user_data: UserCreate) -> UserResponseCreation:
    """Create a new user"""
    try:
        # Ensure MongoDB is connected
        if not db.is_connected:
            connected = await connect_to_mongo()
            if not connected:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not connect to database"
                )

        users_collection = db.get_collection("users")

        # Check if email already exists
        existing_email = await users_collection.find_one({"email": user_data.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check if username already exists
        existing_username = await users_collection.find_one({"username": user_data.username})
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Prepare user document
        user_doc = {
            "email": user_data.email,
            "username": user_data.username,
            "avatar_url": user_data.avatar_url,
            "created_at": datetime.utcnow(),
            "is_active": True
        }

        user_doc = UserBaseDB(
            email=user_data.email,
            username=user_data.username,
            ground_photo="",
            aerial_photo="",
            avatar_url=user_data.avatar_url or "",
            carbon_score=0,
            potential_earnings=None,
            interested_companies=0,
            verification_status=VerificationStatusEnum.PENDING,
            notification_preferences={},
            carbon_journey=None,
            is_verified=False,
            is_active=True
        ).model_dump()

        # Insert the user
        result = await users_collection.insert_one(user_doc)
        # Get the created user
        created_user = await users_collection.find_one({"_id": result.inserted_id})
        return serialize_user(created_user)

    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


async def update_user(user_id: str, user_update: UserUpdate):
    """Update user information"""
    try:
        users_collection = db.get_collection("users")

        # Convert user_update to dict, excluding unset fields
        update_data = user_update.model_dump(exclude_unset=True)

        if not update_data:
            # Nothing to update
            return await get_user(user_id)

        # Check if user exists
        existing_user = await get_user(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update the user
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        if result.modified_count == 0 and result.matched_count > 0:
            # User found but not modified (might be the same data)
            logger.info(f"User {user_id} found but not modified")

        # Return the updated user
        return await get_user(user_id)

    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


async def delete_user(user_id: str):
    """Delete a user"""
    try:
        users_collection = db.get_collection("users")

        # Get user first to return data after deletion
        user = await get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Delete the user
        result = await users_collection.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )
