from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

# Base Company model with shared attributes
class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[HttpUrl] = None
    status: str = "active"  # Default status
    founded_year: Optional[int] = None
    location: Optional[str] = None
    employees_count: Optional[int] = None

# Model for creating a new company
class CompanyCreate(CompanyBase):
    pass

# Model for updating company info - all fields optional
class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[HttpUrl] = None
    status: Optional[str] = None
    founded_year: Optional[int] = None
    location: Optional[str] = None
    employees_count: Optional[int] = None

# Complete company model returned from API
class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True
