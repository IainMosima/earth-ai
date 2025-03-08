from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Dict, Any, Optional, List

from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.s3_utils import delete_file_from_s3
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

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

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
