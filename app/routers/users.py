from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.crud import user_crud
from app.database import get_db

from app.s3_utils import upload_file_to_s3
from app.schemas.user_schemas import UserCreate, UserSchema

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=UserSchema)
async def create_user(
    name: str = Form(...), 
    email: str = Form(...),
    notification_preferences: str = Form("{}"),
    ground_photo: Optional[UploadFile] = File(None),
    aerial_photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Check if user with email already exists
    db_user = user_crud.get_user_by_email(db, email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Parse notification preferences
    try:
        notification_prefs = json.loads(notification_preferences)
    except json.JSONDecodeError:
        notification_prefs = {}
    
    # Create user first
    user_data = UserCreate(
        name=name,
        email=email,
        notification_preferences=notification_prefs
    )
    user = user_crud.create_user(db, user_data)
    
    # Process photo uploads if provided
    if ground_photo:
        result = await upload_file_to_s3(ground_photo, folder=f"users/{user.id}/ground")
        user = user_crud.update_user_photo(db, user.id, "ground", result["key"])
    
    if aerial_photo:
        result = await upload_file_to_s3(aerial_photo, folder=f"users/{user.id}/aerial")
        user = user_crud.update_user_photo(db, user.id, "aerial", result["key"])
    
    return user

@router.get("/", response_model=List[UserSchema])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserSchema)
def read_user(user_id: int, db: Session = Depends(get_db)):
    return user_crud.get_user_by_id(db, user_id)

@router.patch("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    carbon_score: Optional[float] = Form(None),
    potential_earnings: Optional[str] = Form(None),
    interested_companies: Optional[int] = Form(None),
    verification_status: Optional[str] = Form(None),
    notification_preferences: Optional[str] = Form(None),
    carbon_journey: Optional[str] = Form(None),
    ground_photo: Optional[UploadFile] = File(None),
    aerial_photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Get the existing user
    existing_user = user_crud.get_user_by_id(db, user_id)
    
    # Prepare update data
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if email is not None:
        update_data["email"] = email
    if carbon_score is not None:
        update_data["carbon_score"] = carbon_score
    if potential_earnings is not None:
        update_data["potential_earnings"] = potential_earnings
    if interested_companies is not None:
        update_data["interested_companies"] = interested_companies
    if verification_status is not None:
        update_data["verification_status"] = verification_status
        
    # Parse JSON fields if provided
    if notification_preferences is not None:
        try:
            update_data["notification_preferences"] = json.loads(notification_preferences)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON for notification_preferences")
            
    if carbon_journey is not None:
        try:
            update_data["carbon_journey"] = json.loads(carbon_journey)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON for carbon_journey")
    
    # Update user data first
    if update_data:
        user = user_crud.update_user(db, user_id, update_data)
    else:
        user = existing_user
    
    # Process photo uploads if provided
    if ground_photo:
        result = await upload_file_to_s3(ground_photo, folder=f"users/{user_id}/ground")
        user = user_crud.update_user_photo(db, user_id, "ground", result["key"])
    
    if aerial_photo:
        result = await upload_file_to_s3(aerial_photo, folder=f"users/{user_id}/aerial")
        user = user_crud.update_user_photo(db, user_id, "aerial", result["key"])
    
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_crud.delete_user(db, user_id)
