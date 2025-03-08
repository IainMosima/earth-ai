from fastapi import APIRouter, HTTPException, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.database import get_db_session
from app.models.S3 import S3SignedURLs
from app.services.email_service import email_service
from app.services.storage_service import storage_service
from app.models.user import UserResponseCreation, UserResponse, UserCreate, UserUpdate
from app.models.user_model import User
from app.crud.user_crud import create_user, get_user_by_email, update_user, get_user

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/register", response_model=UserResponseCreation)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db_session)):  
    try:
        email = user_data.email
        username = user_data.username
        
        # Check if user already exists
        existing_user = get_user_by_email(db, email)
        
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
            "email": email,
            "username": username,
        }
        
        user = await create_user(db, user_dict)
        
        # Generate signed URLs for photo uploads
        try:
            signed_urls_response = await storage_service.generate_signed_urls(str(user.id))
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
                id=user.id,
                email=user.email,
                username=user.username,
                upload_urls=urls,
                is_verified=user.is_verified,
                created_at=user.created_at
            )
        except Exception as e:
            # Cleanup on failure
            db.delete(user)
            db.commit()
            raise HTTPException(status_code=500, detail=f"Failed to generate upload URLs: {str(e)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.put("/{user_id}", response_model=UserResponse)
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

@router.put("/{user_id}/photos", response_model=UserResponse)
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
