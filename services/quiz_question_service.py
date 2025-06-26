from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.database import QuizQuestion
from models.quiz_question_model import QuizQuestionCreate, QuizQuestionUpdate, QuizQuestionResponse

def create_question(db: Session, question_data: QuizQuestionCreate) -> QuizQuestionResponse:
    question = QuizQuestion(**question_data.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return QuizQuestionResponse.model_validate(question)

def get_all_questions(db: Session):
    return db.query(QuizQuestion).all()

def get_question_by_id(db: Session, question_id: int) -> type[QuizQuestion]:
    question = db.query(QuizQuestion).filter_by(id=question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

def update_question(db: Session, question_id: int, update_data: QuizQuestionUpdate) -> QuizQuestionResponse:
    question = get_question_by_id(db, question_id)

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(question, field, value)

    db.commit()
    db.refresh(question)
    return QuizQuestionResponse.model_validate(question)

def delete_question(db: Session, question_id: int):
    question = get_question_by_id(db, question_id)
    db.delete(question)
    db.commit()