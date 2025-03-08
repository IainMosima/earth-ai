from fastapi import APIRouter, HTTPException, Body, Depends, status
from typing import Dict
import os
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.S3 import S3Callback
from app.models.user_model import User
from app.services.email_service import email_service

router = APIRouter(tags=["webhooks"])

@router.post("/s3-upload-complete")
async def s3_upload_complete(payload: S3Callback, db: Session = Depends(get_db)):
    try:
        with db as session:
            user_id = payload.user_id
            ground_photo_url = payload.ground_photo_url
            ground_photo_key = payload.ground_photo_key
            aerial_photo_url = payload.aerial_photo_url
            aerial_photo_key = payload.aerial_photo_key
            
            # Find the user
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"User not found with ID: {user_id}"
                )
            
            bucket_name = os.getenv('S3_BUCKET_NAME')
            
            # Update user record based on which photo was uploaded
            if ground_photo_url or ground_photo_key:
                user.ground_photo = ground_photo_url
                print(f"Updated ground photo for user {user_id}: {ground_photo_url}")
            
            if aerial_photo_url or aerial_photo_key:
                user.aerial_photo = aerial_photo_url
                print(f"Updated aerial photo for user {user_id}: {aerial_photo_url}")
        
            # Check if registration is now complete
            # if user.ground_photo and user.aerial_photo:
            #     user.registration_complete = True
            #     # Send completion email
            #     await email_service.send_registration_completion_email(user.email)
            
            # Commit changes to DB
            session.commit()
            
            return {
                "message": f"User {user_id} has completed uploading photos",
                "updated": {
                    "ground_photo": bool(ground_photo_url or ground_photo_key),
                    "aerial_photo": bool(aerial_photo_url or aerial_photo_key)
                }
            }
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions as-is
        raise http_ex
    except Exception as e:
        print(f"Upload webhook error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Server error processing upload: {str(e)}"
        )
