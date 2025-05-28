from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.investor_profile_model import (
    InvestorProfileCreate, InvestorProfileUpdate, InvestorProfileResponse
)
from services.investor_profile_service import (
    create_profile, get_all_profiles, get_profile_by_id,
    update_profile, delete_profile
)

router = APIRouter()

@router.post("/", response_model=InvestorProfileResponse, status_code=status.HTTP_201_CREATED)
def create(profile: InvestorProfileCreate, db: Session = Depends(get_db)):
    return create_profile(db, profile)

@router.get("/", response_model=list[InvestorProfileResponse])
def get_all(db: Session = Depends(get_db)):
    return get_all_profiles(db)

@router.get("/{profile_id}", response_model=InvestorProfileResponse)
def get_one(profile_id: int, db: Session = Depends(get_db)):
    return get_profile_by_id(db, profile_id)

@router.put("/{profile_id}", response_model=InvestorProfileResponse)
def update(profile_id: int, profile_data: InvestorProfileUpdate, db: Session = Depends(get_db)):
    return update_profile(db, profile_id, profile_data)

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(profile_id: int, db: Session = Depends(get_db)):
    delete_profile(db, profile_id)