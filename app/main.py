from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db, wait_for_db
from app.routers import users, companies

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
    os.getenv("FRONTEND_URL", "")  # From environment variables
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(companies.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Earth AI API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
