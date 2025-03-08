from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status
from typing import Dict, Any, Optional, List
import os
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
    user_data: Dict[str, Any]
) -> User:
    # Create new user with photo paths
    db_user = User(
        email=user_data["email"],
        username=user_data["username"],
        avatar_url=user_data.get("avatar_url", "")
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        # If database operation fails, cleanup uploaded files
        if os.path.exists(ground_photo_path):
            os.remove(ground_photo_path)
        if os.path.exists(aerial_photo_path):
            os.remove(aerial_photo_path)
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
