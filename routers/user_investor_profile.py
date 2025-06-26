from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.user_investor_profile_model import UserInvestorProfileResponse
from services.user_investor_profile_service import get_user_investor_profiles

router = APIRouter()

@router.get("/{user_id}", response_model=List[UserInvestorProfileResponse])
def retrieve_investor_profile(user_id: int, db: Session = Depends(get_db)):
    return get_user_investor_profiles(db, user_id)