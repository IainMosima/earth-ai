from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Dict, Any, Optional, List

from ..models import Company
from ..schemas import CompanyCreate, CompanyUpdate

def create_company(db: Session, company_data: CompanyCreate) -> Company:
    db_company = Company(
        name=company_data.name,
        tagline=company_data.tagline,
        minimum_score=company_data.minimum_score,
        maximum_score=company_data.maximum_score,
        price_per_credit=company_data.price_per_credit,
        potential_earnings=company_data.potential_earnings,
        status=company_data.status
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_companies(db: Session, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Company]:
    query = db.query(Company)
    
    if status:
        query = query.filter(Company.status == status)
        
    return query.offset(skip).limit(limit).all()

def get_company_by_id(db: Session, company_id: int) -> Optional[Company]:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with id {company_id} not found")
    return company

def update_company(db: Session, company_id: int, company_data: Dict[str, Any]) -> Company:
    company = get_company_by_id(db, company_id)
    
    # Validate maximum_score >= minimum_score if both are provided
    if 'minimum_score' in company_data and 'maximum_score' in company_data:
        if company_data['maximum_score'] < company_data['minimum_score']:
            raise HTTPException(
                status_code=400, 
                detail="Maximum score must be greater than or equal to minimum score"
            )
    # If only one is updated, check against existing value
    elif 'minimum_score' in company_data and company_data['minimum_score'] > company.maximum_score:
        raise HTTPException(
            status_code=400, 
            detail="Minimum score cannot be greater than existing maximum score"
        )
    elif 'maximum_score' in company_data and company_data['maximum_score'] < company.minimum_score:
        raise HTTPException(
            status_code=400, 
            detail="Maximum score cannot be less than existing minimum score"
        )
    
    for key, value in company_data.items():
        setattr(company, key, value)
    
    db.commit()
    db.refresh(company)
    return company

def delete_company(db: Session, company_id: int) -> Dict[str, bool]:
    company = get_company_by_id(db, company_id)
    db.delete(company)
    db.commit()
    return {"success": True}
