from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile as StarletteUploadFile
import shutil

from app.database import engine, Base, get_db, wait_for_db
from app.routes import webhooks, users
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Earth AI API",
    description="API for Earth AI platform",
    version="0.1.0"
)

# Create database tables
@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection and create tables"""
    if wait_for_db():
        try:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # React default
    "http://localhost:8000",  # API itself
    os.getenv("FRONTEND_URL", "http://localhost:3000")  # From environment variables
]

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure custom middleware for large file uploads
@app.middleware("http")
async def custom_upload_middleware(request: Request, call_next):
    # Use environment variables for upload limits with fallback values
    max_upload_size = int(os.getenv("MAX_UPLOAD_SIZE", 104857600))  # From .env: 100MB
    chunk_size = int(os.getenv("CHUNK_SIZE", 1048576))  # From .env: 1MB
    boundary_buffer = int(os.getenv("BOUNDARY_BUFFER_SIZE", 102400))  # From .env: 100KB
    
    # Increase upload limits
    request.scope["max_upload_size"] = max_upload_size
    request.scope["max_form_parts"] = 1000
    request.scope["max_form_field_size"] = chunk_size
    
    # Increase boundary buffer
    if "content-type" in request.headers:
        request.scope["_boundary_buffer_size"] = boundary_buffer
    
    response = await call_next(request)
    return response

# Include routers
app.include_router(users.router)  # No need to specify tags as they're already set in the router
app.include_router(webhooks.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Earth AI API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
