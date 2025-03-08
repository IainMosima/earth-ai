from fastapi import APIRouter, HTTPException, Depends, Path, Form, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import os
import shutil

from app.database import get_db_session, get_db
from app.models.S3 import S3SignedURLs
from app.services.email_service import email_service
from app.services.storage_service import storage_service
from app.models.user import UserResponseCreation, UserResponse, UserCreate, UserUpdate
from app.models.user_model import User
from app.crud.user_crud import create_user, get_user_by_email, update_user, get_user, get_users

router = APIRouter(tags=["users"])

# Make sure we have both prefixes covered
@router.post("/api/users/register", response_model=UserResponseCreation)
async def register_user(
    user : UserCreate,
    db: Session = Depends(get_db_session)
):  
    try:
        # Check if user already exists
        existing_user = get_user_by_email(db, user.email)
        
        if existing_user:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "User already exists"
                }
            )
        
        # Create new user using the CRUD function
        user_dict = {
            "email": user.email,
            "username": user.username,
            "avatar_url": user.avatar_url
        }
        
        # Process uploaded files if provided
        ground_photo_path = ""
        aerial_photo_path = ""
        
        # # Save ground photo if provided
        # if ground_photo:
        #     uploads_dir = "uploads/"
        #     if not os.path.exists(uploads_dir):
        #         os.makedirs(uploads_dir)
                
        #     ground_photo_path = os.path.join(uploads_dir, f"ground_{username}_{ground_photo.filename}")
        #     with open(ground_photo_path, "wb") as buffer:
        #         contents = await ground_photo.read()
        #         buffer.write(contents)
        #     user_dict["ground_photo"] = ground_photo_path
        
        # # Save aerial photo if provided
        # if aerial_photo:
        #     uploads_dir = "uploads/"
        #     if not os.path.exists(uploads_dir):
        #         os.makedirs(uploads_dir)
                
        #     aerial_photo_path = os.path.join(uploads_dir, f"aerial_{username}_{aerial_photo.filename}")
        #     with open(aerial_photo_path, "wb") as buffer:
        #         contents = await aerial_photo.read()
        #         buffer.write(contents)
        #     user_dict["aerial_photo"] = aerial_photo_path
        
        # Create user
        user = await create_user(db, user_dict)
        
        # Generate signed URLs for photo uploads
        try:
            signed_urls_response = await storage_service.generate_signed_urls(user.id)
            # Convert the SignedUrlsResponse to a dictionary
            urls = S3SignedURLs(
                ground_photo_signed=signed_urls_response.ground_photo_signed,
                aerial_photo_signed=signed_urls_response.aerial_photo_signed,
                ground_photo_url=signed_urls_response.ground_photo_url,
                ground_photo_key=signed_urls_response.ground_photo_key,
                aerial_photo_url=signed_urls_response.aerial_photo_url,
                aerial_photo_key=signed_urls_response.aerial_photo_key,
                user_id=user.id,
                created_at=signed_urls_response.created_at
            )
            
            # Return successful response
            return UserResponseCreation(
                id=str(user.id),
                username=user.username,
                email=user.email,
                name=user.username,
                role="user",
                created_at=str(user.created_at),
                upload_urls=urls
            )
        except Exception as e:
            # Cleanup on failure
            db.delete(user)
            db.commit()
            raise HTTPException(status_code=500, detail=f"Failed to generate upload URLs: {str(e)}")
        
    except Exception as e:
        # Clean up any partially created files in case of error
        for path in [ground_photo_path, aerial_photo_path]:
            if path and os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.get("/api/users", response_model=List[UserResponse])
@router.get("/users/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/api/users/{user_id}", response_model=UserResponse)
@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db_session)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/api/users/{user_id}", response_model=UserResponse)
@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: int = Path(..., title="The ID of the user to update"),
    user_data: UserUpdate = None,
    db: Session = Depends(get_db_session)
):
    """
    Update a user's information.
    This can be used to update any user fields, including photo URLs.
    """
    try:
        # Check if the user exists
        existing_user = get_user(db, user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Update the user
        updated_user = update_user(db, user_id, user_data)
        
        # Return the updated user
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            ground_photo=updated_user.ground_photo,
            aerial_photo=updated_user.aerial_photo,
            is_verified=updated_user.is_verified,
            created_at=updated_user.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.put("/api/users/{user_id}/photos", response_model=UserResponse)
async def update_user_photos(
    user_id: int = Path(..., title="The ID of the user to update"),
    ground_photo: Optional[str] = None,
    aerial_photo: Optional[str] = None,
    db: Session = Depends(get_db_session)
):
    """
    Update a user's photos.
    This endpoint is specifically for updating photos after upload.
    """
    try:
        # Check if the user exists
        existing_user = get_user(db, user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Create update data with only the photo fields
        update_data = UserUpdate(
            ground_photo=ground_photo,
            aerial_photo=aerial_photo
        )
        
        # Update the user
        updated_user = update_user(db, user_id, update_data)
        
        # Return the updated user
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            ground_photo=updated_user.ground_photo,
            aerial_photo=updated_user.aerial_photo,
            is_verified=updated_user.is_verified,
            created_at=updated_user.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Photo update failed: {str(e)}")
