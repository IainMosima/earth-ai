from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.crud import user_crud
from app.schemas.user_schemas import UserSchema, UserCreate, UserUpdate
from app.s3_utils import upload_file_to_s3

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = user_crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    return user_crud.create_user(db=db, user=user)

@router.get("/", response_model=List[UserSchema])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserSchema)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return user_crud.update_user(db=db, user_id=user_id, user=user)

@router.delete("/{user_id}", response_model=UserSchema)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_crud.delete_user(db=db, user_id=user_id)

@router.post("/{user_id}/avatar", response_model=UserSchema)
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Upload file to S3
    avatar_url = await upload_file_to_s3(file, folder=f"avatars/{user_id}")
    if not avatar_url:
        raise HTTPException(status_code=500, detail="Failed to upload avatar")
    
    # Update user with new avatar URL
    user_update = UserUpdate(avatar_url=avatar_url)
    return user_crud.update_user(db=db, user_id=user_id, user=user_update)
