from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.user_answer_model import (
    UserAnswerCreate, UserAnswerResponse
)
from services.user_answer_service import (
    create_user_answer, get_user_answers_by_user_id
)

router = APIRouter()

@router.post("/", response_model=UserAnswerResponse, status_code=status.HTTP_201_CREATED)
def create(data: UserAnswerCreate, db: Session = Depends(get_db)):
    return create_user_answer(db, data)

@router.get("/{user_id}", response_model=list[UserAnswerResponse])
def get_by_user(user_id: int, db: Session = Depends(get_db)):
    return get_user_answers_by_user_id(db, user_id)