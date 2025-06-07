from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.user_answer_model import UserAnswerResponse
from services.user_answer_service import get_user_answers_by_user_id

router = APIRouter()

@router.get("/{user_id}", response_model=list[UserAnswerResponse])
def get_by_user(user_id: int, db: Session = Depends(get_db)):
    return get_user_answers_by_user_id(db, user_id)