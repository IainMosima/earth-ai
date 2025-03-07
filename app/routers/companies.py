from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os

# Add these missing imports
from app.models.company import CompanyModel
from app.schemas.company import Company, CompanyCreate, CompanyUpdate

from app.crud import company_crud
from app.database import get_db

router = APIRouter(
    prefix="/companies",
    tags=["companies"]
)

@router.post("/", response_model=Company)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    return company_crud.create_company(db, company)

@router.get("/", response_model=List[Company])
def read_companies(status: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = company_crud.get_companies(db, status=status, skip=skip, limit=limit)
    return companies

@router.get("/{company_id}", response_model=Company)
def read_company(company_id: int, db: Session = Depends(get_db)):
    return company_crud.get_company_by_id(db, company_id)

@router.patch("/{company_id}", response_model=Company)
def update_company(company_id: int, company_data: CompanyUpdate, db: Session = Depends(get_db)):
    # Convert Pydantic model to dict, excluding unset fields
    update_data = company_data.dict(exclude_unset=True)
    return company_crud.update_company(db, company_id, update_data)

@router.delete("/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    return company_crud.delete_company(db, company_id)

def seed_companies_task(db: Session):
    data_path = os.path.join(os.getcwd(), "data", "companies.json")
    
    try:
        with open(data_path, 'r') as file:
            companies_data = json.load(file)
        
        for company_data in companies_data:
            # Check if company already exists by name to avoid duplicates
            existing = db.query(CompanyModel).filter(CompanyModel.name == company_data["name"]).first()
            if existing:
                continue
                
            # Create company from data
            create_data = CompanyCreate(**company_data)
            company_crud.create_company(db, create_data)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error seeding companies: {str(e)}")

@router.post("/seed")
def seed_companies(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Run the seeding task in the background
    background_tasks.add_task(seed_companies_task, db)
    return {"message": "Company seeding started in the background"}
