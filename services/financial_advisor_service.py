import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.database import FinancialAdvisor
from models.financial_advisor_model import FinancialAdvisorCreate, FinancialAdvisorResponse, FinancialAdvisorUpdate
from services.auth_service import hash_password

logger = logging.getLogger(__name__)

def create_advisor(db: Session, advisor_data: FinancialAdvisorCreate) -> FinancialAdvisorResponse:
    """Create a new financial advisor."""
    existing = db.query(FinancialAdvisor).filter_by(email=advisor_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = hash_password(advisor_data.password)
    advisor = FinancialAdvisor(
        name=advisor_data.name,
        email=str(advisor_data.email),
        password=hashed_password
    )
    db.add(advisor)
    db.commit()
    db.refresh(advisor)
    
    return FinancialAdvisorResponse.model_validate(advisor)

def get_all_advisors(db: Session):
    return db.query(FinancialAdvisor).all()

def get_advisor_by_id(db: Session, advisor_id: int) -> type[FinancialAdvisor]:
    advisor = db.query(FinancialAdvisor).filter_by(id=advisor_id).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Advisor not found")
    return advisor

def update_advisor(db: Session, advisor_id: int, update_data: FinancialAdvisorUpdate) -> FinancialAdvisorResponse:
    advisor = get_advisor_by_id(db, advisor_id)
    
    if update_data.name:
        advisor.name = update_data.name
    if update_data.email:
        advisor.email = update_data.email
    if update_data.password:
        advisor.password = hash_password(update_data.password)

    db.commit()
    db.refresh(advisor)
    
    return FinancialAdvisorResponse.model_validate(advisor)

def delete_advisor(db: Session, advisor_id: int):
    advisor = db.query(FinancialAdvisor).filter_by(id=advisor_id).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Advisor not found")
    db.delete(advisor)
    db.commit()