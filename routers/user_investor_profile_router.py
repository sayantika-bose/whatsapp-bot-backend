from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.user_investor_profile_model import UserInvestorProfileResponse
from services.user_investor_profile_service import calculate_and_save_user_profile, get_user_investor_profiles

router = APIRouter()


@router.post("/{user_id}", response_model=list[UserInvestorProfileResponse])
def calculate_user_profile(user_id: int, db: Session = Depends(get_db)):
    return calculate_and_save_user_profile(db, user_id)

@router.get("/{user_id}", response_model=List[UserInvestorProfileResponse])
def retrieve_user_profile(user_id: int, db: Session = Depends(get_db)):
    return get_user_investor_profiles(db, user_id)