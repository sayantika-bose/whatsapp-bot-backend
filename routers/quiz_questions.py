from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.quiz_question_model import QuizQuestionCreate, QuizQuestionUpdate, QuizQuestionResponse
from services.quiz_question_service import (
    create_question, get_all_questions, get_question_by_id,
    update_question, delete_question
)

router = APIRouter()

# TODO YNA: create the four answers with the question creation
@router.post("/", response_model=QuizQuestionResponse, status_code=status.HTTP_201_CREATED)
def create(question: QuizQuestionCreate, db: Session = Depends(get_db)):
    return create_question(db, question)

@router.get("/", response_model=list[QuizQuestionResponse])
def get_all(db: Session = Depends(get_db)):
    return get_all_questions(db)

@router.get("/{question_id}", response_model=QuizQuestionResponse)
def get_one(question_id: int, db: Session = Depends(get_db)):
    return get_question_by_id(db, question_id)

@router.put("/{question_id}", response_model=QuizQuestionResponse)
def update(question_id: int, question_data: QuizQuestionUpdate, db: Session = Depends(get_db)):
    return update_question(db, question_id, question_data)

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(question_id: int, db: Session = Depends(get_db)):
    delete_question(db, question_id)