import os
import time
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
os.environ.clear()
load_dotenv()

# Get database connection parameters from environment variables with defaults
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")

# Construct the database URL
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=disable"

# Create engine with connection pooling settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=3600,   # Recycle connections after 1 hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a database session
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def wait_for_db(retries=5, delay=2):
    """Attempts to connect to the database with retries"""
    attempt = 0
    last_exception = None
    
    while attempt < retries:
        try:
            # Try to connect
            with engine.connect() as conn:
                print("Successfully connected to the database")
                return True
        except Exception as e:
            last_exception = e
            attempt += 1
            print(f"Database connection attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    
    print(f"Could not connect to the database after {retries} attempts")
    print(f"Last error: {last_exception}")
    return False
