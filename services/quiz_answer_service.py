from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.database import QuizAnswer
from models.quiz_answer_model import QuizAnswerCreate, QuizAnswerUpdate, QuizAnswerResponse
from sqlalchemy.orm import joinedload

def create_answer(db: Session, answer_data: QuizAnswerCreate) -> QuizAnswerResponse:
    existing_answers = db.query(QuizAnswer).filter_by(question_id=answer_data.question_id).count()   
    
    if existing_answers >= 4:
        raise HTTPException(
            status_code=400,
            detail="A question can have a maximum of 4 answers."
        )
        
    answer = QuizAnswer(**answer_data.model_dump())
    
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return QuizAnswerResponse.model_validate(answer)

def get_answers_by_question_id(db: Session, question_id: int):
    return (
        db.query(QuizAnswer)
        .options(joinedload(QuizAnswer.question), joinedload(QuizAnswer.profile))
        .filter(QuizAnswer.question_id == question_id)
        .all()
    )

def get_answer_by_id(db: Session, answer_id: int) -> QuizAnswer:
    answer = db.query(QuizAnswer).filter_by(id=answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Quiz answer not found")
    return answer

def update_answer(db: Session, answer_id: int, update_data: QuizAnswerUpdate) -> QuizAnswerResponse:
    answer = get_answer_by_id(db, answer_id)

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(answer, field, value)

    db.commit()
    db.refresh(answer)
    return QuizAnswerResponse.model_validate(answer)

def delete_answer(db: Session, answer_id: int):
    answer = get_answer_by_id(db, answer_id)
    db.delete(answer)
    db.commit()