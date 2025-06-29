from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from models.quiz_answer_model import QuizAnswerResponse
from models.quiz_question_model import QuizQuestionResponse


class UserAnswerCreate(BaseModel):
    question_id: int
    answer_id: int

class BulkUserAnswerCreate(BaseModel):
    user_id: Optional[int] = None
    answers: List[UserAnswerCreate]

class UserAnswerResponse(BaseModel):
    id: int
    answered_at: datetime
    question: QuizQuestionResponse
    answer: QuizAnswerResponse

    model_config = {
        "from_attributes": True
    }