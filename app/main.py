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
from app.routers import companies
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
    # Increase upload limits
    request.scope["max_upload_size"] = 100 * 1024 * 1024  # 100MB
    request.scope["max_form_parts"] = 1000
    request.scope["max_form_field_size"] = 10 * 1024 * 1024  # 10MB per field
    
    # Increase boundary buffer
    if "content-type" in request.headers:
        request.scope["_boundary_buffer_size"] = 100 * 1024  # 100KB boundary buffer
    
    response = await call_next(request)
    return response

# Include routers
app.include_router(users.router, tags=["users"])
app.include_router(companies.router)
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

@app.get("/")
async def root():
    return {"message": "Welcome to Earth AI API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
