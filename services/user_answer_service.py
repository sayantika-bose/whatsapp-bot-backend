from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from models.database import QuizAnswer, UserAnswer
from models.user_answer_model import UserAnswerCreate, UserAnswerResponse, BulkUserAnswerCreate


def create_bulk_user_answers_service(db: Session, data: BulkUserAnswerCreate) -> List[UserAnswerResponse]:
    user_answers = []
    for answer_data in data.answers:
        # Propagate session_id/user_id to each answer
        answer_dict = answer_data.model_dump()
        answer_dict["session_id"] = data.session_id
        answer_dict["user_id"] = data.user_id
        user_answer = UserAnswer(**answer_dict)
        db.add(user_answer)
        user_answers.append(user_answer)

    db.commit()
    for ua in user_answers:
        db.refresh(ua)

    return [UserAnswerResponse.model_validate(ua) for ua in user_answers]


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