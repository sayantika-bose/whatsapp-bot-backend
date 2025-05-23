from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.financial_advisor_model import FinancialAdvisorCreate, FinancialAdvisorUpdate, FinancialAdvisorResponse
from services.financial_advisor_service import (
    create_advisor, get_all_advisors, get_advisor_by_id,
    update_advisor, delete_advisor
)

router = APIRouter(prefix="/advisors", tags=["Financial Advisors"])

@router.post("/", response_model=FinancialAdvisorResponse, status_code=status.HTTP_201_CREATED)
def create(advisor: FinancialAdvisorCreate, db: Session = Depends(get_db)):
    return create_advisor(db, advisor)

@router.get("/", response_model=list[FinancialAdvisorResponse])
def get_all(db: Session = Depends(get_db)):
    return get_all_advisors(db)

@router.get("/{advisor_id}", response_model=FinancialAdvisorResponse)
def get_one(advisor_id: int, db: Session = Depends(get_db)):
    return get_advisor_by_id(db, advisor_id)

@router.put("/{advisor_id}", response_model=FinancialAdvisorResponse)
def update(advisor_id: int, advisor_data: FinancialAdvisorUpdate, db: Session = Depends(get_db)):
    return update_advisor(db, advisor_id, advisor_data)

@router.delete("/{advisor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(advisor_id: int, db: Session = Depends(get_db)):
    delete_advisor(db, advisor_id)