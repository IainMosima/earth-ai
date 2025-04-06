from fastapi import APIRouter, HTTPException, Depends, status
import os
from sqlalchemy.orm import Session
from app.requests.S3 import S3Callback


router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/s3-upload-complete")
async def s3_upload_complete():
    pass