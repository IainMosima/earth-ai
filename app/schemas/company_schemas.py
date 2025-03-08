from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None

class CompanySchema(CompanyBase):
    id: int
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
