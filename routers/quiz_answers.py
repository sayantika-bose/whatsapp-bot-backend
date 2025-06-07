from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.quiz_answer_model import (
    QuizAnswerUpdate, QuizAnswerResponse, QuizAnswerBatchCreate
)
from services.quiz_answer_service import (
    get_answer_by_id, get_answers_by_question_id,
    update_answer, create_answers
)

router = APIRouter()

@router.post("/{question_id}", response_model=List[QuizAnswerResponse], status_code=status.HTTP_201_CREATED)
def create(
    question_id: int,
    batch: QuizAnswerBatchCreate,
    db: Session = Depends(get_db)
):
    return create_answers(db, question_id, batch.answers)

@router.get("/{question_id}", response_model=list[QuizAnswerResponse])
def get_answers(question_id: int, db: Session = Depends(get_db)):
    return get_answers_by_question_id(db, question_id)

@router.get("/{answer_id}", response_model=QuizAnswerResponse)
def get_one(answer_id: int, db: Session = Depends(get_db)):
    return get_answer_by_id(db, answer_id)

@router.put("/{answer_id}", response_model=QuizAnswerResponse)
def update(answer_id: int, answer_data: QuizAnswerUpdate, db: Session = Depends(get_db)):
    return update_answer(db, answer_id, answer_data)