from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: str
    username: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True
