from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Dict
import os
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.S3 import S3Callback
from app.models.user_model import User
from app.services.email_service import email_service

router = APIRouter()

@router.post("/s3-upload-complete")
async def s3_upload_complete(payload: S3Callback, db: Session = Depends(get_db)):
    try:
        user_id = payload.get("userId")
        ground_photo_url = payload.get("ground_photo_url")
        ground_photo_key = payload.get("ground_photo_key")
        aerial_photo_url = payload.get("aerial_photo_url")
        aerial_photo_key = payload.get("aerial_photo_key")
        created_at = payload.get("created_at")
        
        # Find the user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        bucket_name = os.getenv('S3_BUCKET_NAME')
        
        # Update user record based on which photo was uploaded
        if ground_photo_url or ground_photo_key:
            user.ground_photo = ground_photo_url
        elif aerial_photo_url or aerial_photo_key:
            user.aerial_photo = aerial_photo_url
        
        # Check if registration is now complete
        # if user.ground_photo_url and user.aerial_photo_url:
        #     user.registration_complete = True
        #     # Send completion email
        #     await email_service.send_registration_completion_email(user.email)
        
        db.commit()
        
        return {
            "message": f"User {user_id} ({user.name}) has completed uploading"
        }
    except Exception as e:
        print(f"Upload webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Server error processing upload")
