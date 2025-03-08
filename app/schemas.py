from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, List, Any, Union
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    # notification_preferences: Optional[Dict[str, bool]] = {}
    
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    carbon_score: Optional[float] = None
    potential_earnings: Optional[str] = None
    interested_companies: Optional[int] = None
    verification_status: Optional[str] = None
    notification_preferences: Optional[Dict[str, bool]] = None
    carbon_journey: Optional[List[Dict[str, Any]]] = None

class UserInDB(UserBase):
    id: int
    ground_photo: Optional[str] = None
    aerial_photo: Optional[str] = None
    carbon_score: float = 0
    potential_earnings: Optional[str] = None
    interested_companies: int = 0
    verification_status: str = "Pending"
    notification_preferences: Dict[str, bool] = {}
    carbon_journey: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class User(UserInDB):
    pass

# Company schemas
class CompanyBase(BaseModel):
    name: str
    tagline: Optional[str] = None
    minimum_score: float
    maximum_score: float
    price_per_credit: float
    potential_earnings: float
    status: str = "Pending"
    
    @validator('maximum_score')
    def check_max_score(cls, v, values):
        if 'minimum_score' in values and v < values['minimum_score']:
            raise ValueError('maximum_score must be >= minimum_score')
        return v

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    tagline: Optional[str] = None
    minimum_score: Optional[float] = None
    maximum_score: Optional[float] = None
    price_per_credit: Optional[float] = None
    potential_earnings: Optional[float] = None
    status: Optional[str] = None
    
    @validator('maximum_score')
    def check_max_score(cls, v, values):
        if v is not None and 'minimum_score' in values and values['minimum_score'] is not None and v < values['minimum_score']:
            raise ValueError('maximum_score must be >= minimum_score')
        return v

class CompanyInDB(CompanyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class Company(CompanyInDB):
    pass
