from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.database import QuizAnswer
from models.quiz_answer_model import QuizAnswerCreate, QuizAnswerUpdate, QuizAnswerResponse
from sqlalchemy.orm import joinedload

def create_answers(
    db: Session,
    question_id: int,
    answers_data: List[QuizAnswerCreate]
) -> List[QuizAnswerResponse]:
    if len(answers_data) > 4:
        raise HTTPException(
            status_code=400,
            detail="You can only create up to 4 answers per question."
        )

    existing_count = db.query(QuizAnswer).filter_by(question_id=question_id).count()
    if existing_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Answers for this question already exist. Use update instead."
        )

    created_answers = []
    for answer_data in answers_data:
        answer = QuizAnswer(
            label=answer_data.label,
            text=answer_data.text,
            profile_id=answer_data.profile_id,
            question_id=question_id
        )
        db.add(answer)
        created_answers.append(answer)

    db.commit()

    for answer in created_answers:
        db.refresh(answer)

    return [QuizAnswerResponse.model_validate(a) for a in created_answers]

def get_answers_by_question_id(db: Session, question_id: int):
    return (
        db.query(QuizAnswer)
        .options(joinedload(QuizAnswer.question), joinedload(QuizAnswer.profile))
        .filter(QuizAnswer.question_id == question_id)
        .all()
    )

def get_answer_by_id(db: Session, answer_id: int) -> type[QuizAnswer]:
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