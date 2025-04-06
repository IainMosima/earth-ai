from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List

from app.services.storage_service import storage_service
from app.requests.user import UserResponseCreation, UserResponse, UserCreate, UserUpdate
from app.db.user_repository import create_user, get_user_by_email, update_user, get_user, get_users, delete_user

router = APIRouter(tags=["users"])


# Make sure we have both prefixes covered
@router.post("/api/users/register", response_model=UserResponseCreation)
async def register_user(
        user: UserCreate
):
    try:
        existing_user = await get_user_by_email(user.email)

        if existing_user:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "User already exists"
                }
            )

        user_dict = UserCreate(
            email=user.email,
            username=user.username,
            avatar_url=user.avatar_url,
        )

        # Create user
        created_user = await create_user(user_dict)

        # Generate signed URLs for photo uploads
        try:
            signed_urls = await storage_service.generate_signed_urls(str(created_user["id"]), user.ground_photo_content_type, user.aerial_photo_content_type)
            # Return successful response
            return UserResponseCreation(
                id=str(created_user["id"]),
                email=created_user["email"],
                name=created_user["username"],
                created_at=str(created_user["created_at"]),
                upload_urls=signed_urls
            )

        except Exception as e:
            # Cleanup on failure
            await delete_user(created_user["id"])
            raise HTTPException(status_code=500, detail=f"Failed to generate upload URLs: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")



@router.get("/api/users", response_model=List[UserResponse])
@router.get("/users/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100):
    users = get_users(skip=skip, limit=limit)
    return users


@router.get("/api/users/{user_id}", response_model=UserResponse)
@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: str):
    db_user = get_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/api/users/{user_id}", response_model=UserResponse)
@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
        user_id: str = Path(..., title="The ID of the user to update"),
        user_data: UserUpdate = None
):
    """
    Update a user's information.
    This can be used to update any user fields, including photo URLs.
    """
    try:
        # Check if the user exists
        existing_user = get_user(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update the user
        updated_user = update_user(user_id, user_data)

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
        user_id: str = Path(..., title="The ID of the user to update"),
        ground_photo: Optional[str] = None,
        aerial_photo: Optional[str] = None
):
    """
    Update a user's photos.
    This endpoint is specifically for updating photos after upload.
    """
    try:
        # Check if the user exists
        existing_user = get_user(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create update data with only the photo fields
        update_data = UserUpdate(
            ground_photo=ground_photo,
            aerial_photo=aerial_photo
        )

        # Update the user
        updated_user = update_user(user_id, update_data)

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
