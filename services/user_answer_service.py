from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from models.database import QuizAnswer, UserAnswer
from models.user_answer_model import UserAnswerCreate, UserAnswerResponse, BulkUserAnswerCreate


def create_bulk_user_answers_service(db: Session, data: BulkUserAnswerCreate) -> List[UserAnswerResponse]:
    user_answers = []

    for answer_data in data.answers:
        answer_dict = answer_data.model_dump()
        answer_dict["user_id"] = data.user_id 
        user_answer = UserAnswer(**answer_dict)
        db.add(user_answer)
        user_answers.append(user_answer)

    db.commit()

    user_answer_ids = [ua.id for ua in user_answers]
    
    refreshed_user_answers = (
        db.query(UserAnswer)
        .options(joinedload(UserAnswer.answer), joinedload(UserAnswer.question))
        .filter(UserAnswer.id.in_(user_answer_ids))
        .all()
    )

    return [UserAnswerResponse.model_validate(ua) for ua in refreshed_user_answers]


def get_user_answers_by_user_id(db: Session, user_id: int):
    return (
        db.query(UserAnswer)
        .options(
            joinedload(UserAnswer.answer).joinedload(QuizAnswer.question),
            joinedload(UserAnswer.answer).joinedload(QuizAnswer.profile),
            joinedload(UserAnswer.question)
        )
        .filter(UserAnswer.user_id == user_id)
        .all()
    )