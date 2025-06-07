from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.user_answer_model import BulkUserAnswerCreate, UserAnswerCreate
from models.user_investor_profile_model import UserInvestorProfileResponse, CompleteQuizFlowRequest
from models.user_model import UserCreate
from services.user_answer_service import create_bulk_user_answers_service
from services.user_investor_profile_service import calculate_and_save_user_profile, get_user_investor_profiles
from services.user_service import create_user

router = APIRouter()

@router.post("/complete-flow", response_model=List[UserInvestorProfileResponse])
def complete_quiz_flow(data: CompleteQuizFlowRequest, db: Session = Depends(get_db)):
    # 1. Transform answers into expected type
    transformed_answers = [
        UserAnswerCreate(question_id=a.question_id, answer_id=a.answer_id)
        for a in data.answers
    ]

    # 2. Create user answers with session ID
    user_answers_payload = BulkUserAnswerCreate(
        session_id=data.session_id,
        answers=transformed_answers,
        user_id=None
    )
    create_bulk_user_answers_service(db, user_answers_payload)

    # 3. Create user and link answers from session
    user_data = UserCreate(**data.user.model_dump(), session_id=data.session_id)
    user = create_user(db, user_data)

    # 4. Calculate investor profile from user's answers
    return calculate_and_save_user_profile(db, user.id)

@router.post("/{user_id}", response_model=list[UserInvestorProfileResponse])
def calculate_user_profile(user_id: int, db: Session = Depends(get_db)):
    return calculate_and_save_user_profile(db, user_id)

@router.get("/{user_id}", response_model=List[UserInvestorProfileResponse])
def retrieve_user_profile(user_id: int, db: Session = Depends(get_db)):
    return get_user_investor_profiles(db, user_id)