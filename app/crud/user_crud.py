from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status
from typing import Dict, Any, Optional, List

from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.s3_utils import delete_file_from_s3, upload_file_to_s3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

async def create_user(
    db: Session,
    user_data: UserCreate,
    
) -> User:
    # Upload ground photo to S3
    print("Here")
    ground_photo_result = await upload_file_to_s3(
        user_data.ground_photo,
        folder="user-ground-photos"
    )
    
    # Upload aerial photo to S3
    aerial_photo_result = await upload_file_to_s3(
        user_data.aerial_photo,
        folder="user-aerial-photos"
    )
    
    # Create new user with S3 keys
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        ground_photo_key=ground_photo_result["key"],
        aerial_photo_key=aerial_photo_result["key"]
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        # If database operation fails, cleanup S3 uploaded files
        from app.s3_utils import delete_file_from_s3
        delete_file_from_s3(ground_photo_result["key"])
        delete_file_from_s3(aerial_photo_result["key"])
        raise HTTPException(status_code=500, detail=str(e))

def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update user fields that are provided
    update_data = user.dict(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in update_data:
        update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))
    
    # Handle avatar deletion if needed
    # This would be more complex in a real application
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Delete user's avatar from S3 if exists
    if db_user.avatar_url:
        delete_file_from_s3(db_user.avatar_url)
    
    db.delete(db_user)
    db.commit()
    return db_user
