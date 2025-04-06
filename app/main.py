import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
import logging
import asyncio
from app.routers import users
from app.db import connect_to_mongo, close_mongo_connection

# Load environment variables
load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("app")



# Initialize FastAPI app
app = FastAPI(
    title="Earth AI API",
    description="API for Earth AI platform",
    version="0.1.0"
)

# Create database tables
@app.on_event("startup")
async def startup_db_client():
    logger.info("🚀 Starting application...")
    connection_successful = await connect_to_mongo()

    if not connection_successful:
        logger.error("⚠️ Application started with MongoDB connection issues!")
        # Retrying logic (optional)
        for i in range(3):
            logger.info(f"Retrying connection in 5 seconds (attempt {i + 1}/3)...")
            await asyncio.sleep(5)
            if await connect_to_mongo():
                logger.info("✅ Connection successful on retry!")
                break
    else:
        logger.info("✅ Application started successfully with MongoDB connection!")

 # Close MongoDB connection on shutdown
@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("🛑 Shutting down application...")
    await close_mongo_connection()

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
app.include_router(users.router)
# app.include_router(webhooks.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Earth AI API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
