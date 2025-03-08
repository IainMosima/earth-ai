from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Dict
import os
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.services.email_service import email_service

router = APIRouter()

@router.post("/s3-upload-complete")
async def s3_upload_complete(payload: Dict = Body(...), db: Session = Depends(get_db)):
    try:
        key = payload.get("key")
        user_id = payload.get("userId")
        
        if not key or not user_id:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Find the user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        bucket_name = os.getenv('S3_BUCKET_NAME')
        
        # Update user record based on which photo was uploaded
        if "ground_photo" in key:
            user.ground_photo_url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
        elif "aerial_photo" in key:
            user.aerial_photo_url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
        
        # # Check if registration is now complete
        # if user.ground_photo_url and user.aerial_photo_url:
        #     user.registration_complete = True
        #     # Send completion email
        #     await email_service.send_registration_completion_email(user.email)
        
        # db.commit()
        
        return {"message": "Upload processed successfully"}
    except Exception as e:
        print(f"Upload webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Server error processing upload")
