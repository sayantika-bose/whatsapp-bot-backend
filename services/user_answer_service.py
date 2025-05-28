from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from models.database import QuizAnswer, UserAnswer
from models.user_answer_model import UserAnswerCreate, UserAnswerResponse

def create_user_answer(db: Session, data: UserAnswerCreate) -> UserAnswerResponse:
    user_answer = UserAnswer(**data.model_dump())
    db.add(user_answer)
    db.commit()
    db.refresh(user_answer)
    return UserAnswerResponse.model_validate(user_answer)


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