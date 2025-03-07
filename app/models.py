from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    ground_photo = Column(String, nullable=True)
    aerial_photo = Column(String, nullable=True)
    carbon_score = Column(Float, default=0)
    potential_earnings = Column(String, nullable=True)
    interested_companies = Column(Integer, default=0)
    verification_status = Column(String, default="Pending")
    notification_preferences = Column(JSON, default={})
    carbon_journey = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tagline = Column(String, nullable=True)
    minimum_score = Column(Float, nullable=False)
    maximum_score = Column(Float, nullable=False)
    price_per_credit = Column(Float, nullable=False)
    potential_earnings = Column(Float, nullable=False)
    status = Column(String, default="Pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
