from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil

from app.database import get_db
from app.crud import user_crud
from app.schemas.user_schemas import UserSchema, UserCreate, UserUpdate
import os

router = APIRouter(prefix="/users", tags=["users"])

UPLOAD_DIR = "uploads/"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/", response_model=UserSchema)
async def create_user(
    email: str = Form(...),
    username: str = Form(...),
    ground_photo: UploadFile = File(None),  # Make file optional to help debug
    aerial_photo: UploadFile = File(None),  # Make file optional to help debug
    avatar_url: str = Form(""),  # Default empty string instead of None
    db: Session = Depends(get_db),
):
    # Use the db session correctly by entering the context manager
    with db as session:
        # Check for existing user
        if user_crud.get_user_by_email(session, email=email):
            raise HTTPException(status_code=400, detail="Email already registered")
        if user_crud.get_user_by_username(session, username=username):
            raise HTTPException(status_code=400, detail="Username already taken")

        try:
            ground_photo_path = ""
            aerial_photo_path = ""
            
            # Save ground photo if provided
            if ground_photo:
                ground_photo_path = os.path.join(UPLOAD_DIR, f"ground_{username}_{ground_photo.filename}")
                with open(ground_photo_path, "wb") as buffer:
                    contents = ground_photo.file.read()
                    buffer.write(contents)
                ground_photo.file.close()
            
            # Save aerial photo if provided
            if aerial_photo:
                aerial_photo_path = os.path.join(UPLOAD_DIR, f"aerial_{username}_{aerial_photo.filename}")
                with open(aerial_photo_path, "wb") as buffer:
                    contents = aerial_photo.file.read()
                    buffer.write(contents)
                aerial_photo.file.close()
            
            # Create user in DB
            user_data = {
                "email": email,
                "username": username,
                "ground_photo": ground_photo_path,
                "aerial_photo": aerial_photo_path,
                "avatar_url": avatar_url,
            }

            # If user_crud.create_user is async, add await:
            # user = await user_crud.create_user(db=session, user_data=user_data)
            # Otherwise, keep as is:
            user = await user_crud.create_user(db=session, user_data=user_data)
            
            # Make sure we're returning the actual user object, not a coroutine
            return user
        
        except Exception as e:
            # Clean up any partially created files in case of error
            for path in [ground_photo_path, aerial_photo_path]:
                if path and os.path.exists(path):
                    os.remove(path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )

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

# @router.post("/{user_id}/avatar", response_model=UserSchema)
# async def upload_avatar(
#     user_id: int,
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     db_user = user_crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     # Upload file to S3
#     avatar_url = await upload_file_to_s3(file, folder=f"avatars/{user_id}")
#     if not avatar_url:
#         raise HTTPException(status_code=500, detail="Failed to upload avatar")
    
#     # Update user with new avatar URL
#     user_update = UserUpdate(avatar_url=avatar_url)
#     return user_crud.update_user(db=db, user_id=user_id, user=user_update)
