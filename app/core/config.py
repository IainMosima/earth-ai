from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    CHUNK_SIZE: int = 1024 * 1024  # 1MB chunks
    BOUNDARY_BUFFER_SIZE: int = 100 * 1024  # 100KB
    
    # SQLAlchemy configuration
    SQLALCHEMY_CONFIG: dict = {"__allow_unmapped__": True}
    
    class Config:
        env_file = ".env"
        # Updated to use the newer Pydantic V2 config names
        populate_by_name = True
        json_schema_extra = {"title": "Earth AI API Settings"}

settings = Settings()