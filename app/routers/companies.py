from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.company_model import Company
from app.schemas.company_schemas import CompanySchema, CompanyCreate, CompanyUpdate
from app.s3_utils import upload_file_to_s3, delete_file_from_s3

router = APIRouter(prefix="/companies", tags=["companies"])

@router.post("/", response_model=CompanySchema)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.get("/", response_model=List[CompanySchema])
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies

@router.get("/{company_id}", response_model=CompanySchema)
def read_company(company_id: int, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.put("/{company_id}", response_model=CompanySchema)
def update_company(company_id: int, company: CompanyUpdate, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    update_data = company.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_company, key, value)
    
    db.commit()
    db.refresh(db_company)
    return db_company

@router.delete("/{company_id}", response_model=CompanySchema)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Delete company logo if exists
    if db_company.logo_url:
        delete_file_from_s3(db_company.logo_url)
    
    db.delete(db_company)
    db.commit()
    return db_company

@router.post("/{company_id}/logo", response_model=CompanySchema)
async def upload_logo(
    company_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Upload file to S3
    logo_url = await upload_file_to_s3(file, folder=f"logos/{company_id}")
    if not logo_url:
        raise HTTPException(status_code=500, detail="Failed to upload logo")
    
    # Update company with new logo URL
    db_company.logo_url = logo_url
    db.commit()
    db.refresh(db_company)
    return db_company
