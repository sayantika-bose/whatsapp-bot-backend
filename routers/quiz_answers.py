from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.quiz_answer_model import (
    QuizAnswerCreate, QuizAnswerUpdate, QuizAnswerResponse
)
from services.quiz_answer_service import (
    create_answer, get_answer_by_id, get_answers_by_question_id,
    update_answer, delete_answer
)

router = APIRouter()

@router.post("/", response_model=QuizAnswerResponse, status_code=status.HTTP_201_CREATED)
def create(answer: QuizAnswerCreate, db: Session = Depends(get_db)):
    return create_answer(db, answer)

@router.get("/{question_id}", response_model=list[QuizAnswerResponse])
def get_answers(question_id: int, db: Session = Depends(get_db)):
    return get_answers_by_question_id(db, question_id)

@router.get("/{answer_id}", response_model=QuizAnswerResponse)
def get_one(answer_id: int, db: Session = Depends(get_db)):
    return get_answer_by_id(db, answer_id)

@router.put("/{answer_id}", response_model=QuizAnswerResponse)
def update(answer_id: int, answer_data: QuizAnswerUpdate, db: Session = Depends(get_db)):
    return update_answer(db, answer_id, answer_data)

@router.delete("/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(answer_id: int, db: Session = Depends(get_db)):
    delete_answer(db, answer_id)