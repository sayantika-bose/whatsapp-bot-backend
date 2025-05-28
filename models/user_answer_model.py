from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from models.quiz_answer_model import QuizAnswerResponse
from models.quiz_question_model import QuizQuestionResponse

class UserAnswerCreate(BaseModel):
    user_id: int
    question_id: int
    answer_id: int

class UserAnswerUpdate(BaseModel):
    user_id: Optional[int] = None
    question_id: Optional[int] = None
    answer_id: Optional[int] = None

class UserAnswerResponse(BaseModel):
    id: int
    answered_at: datetime
    question: QuizQuestionResponse
    answer: QuizAnswerResponse

    model_config = {
        "from_attributes": True
    }