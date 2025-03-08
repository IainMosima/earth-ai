from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db_session
from app.services.email_service import email_service
from app.services.storage_service import storage_service
from app.models.user import UserResponseCreation, UserResponse, UserCreate
from app.models.user_model import User

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/register", response_model=UserResponseCreation)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db_session)):  
    try:
        email = user_data.email
        username = user_data.username
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "User already exists"
                }
            )
        
        # Create new user
        user = User(
            email=email,
            username=username,
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Generate signed URLs for photo uploads
        try:
            urls = await storage_service.generate_signed_urls(str(user.id))
            
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
