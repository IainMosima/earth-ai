from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Dict, Any, Optional, List

from ..models import User
from ..schemas import UserCreate, UserUpdate
from ..s3_utils import delete_file_from_s3

def create_user(db: Session, user_data: UserCreate) -> User:
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        notification_preferences=user_data.notification_preferences
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def update_user(db: Session, user_id: int, user_data: Dict[str, Any]) -> User:
    user = get_user_by_id(db, user_id)
    
    for key, value in user_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> Dict[str, bool]:
    user = get_user_by_id(db, user_id)
    
    # Optionally delete S3 objects
    if user.ground_photo:
        delete_file_from_s3(user.ground_photo)
    if user.aerial_photo:
        delete_file_from_s3(user.aerial_photo)
    
    db.delete(user)
    db.commit()
    return {"success": True}

def update_user_photo(db: Session, user_id: int, photo_type: str, photo_key: str) -> User:
    user = get_user_by_id(db, user_id)
    
    # Delete old photo if it exists
    if photo_type == "ground" and user.ground_photo:
        delete_file_from_s3(user.ground_photo)
    elif photo_type == "aerial" and user.aerial_photo:
        delete_file_from_s3(user.aerial_photo)
    
    # Update with new photo
    if photo_type == "ground":
        user.ground_photo = photo_key
    elif photo_type == "aerial":
        user.aerial_photo = photo_key
    
    db.commit()
    db.refresh(user)
    return user
