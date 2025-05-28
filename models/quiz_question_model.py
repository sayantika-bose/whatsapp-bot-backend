from pydantic import BaseModel
from typing import Optional

class QuizQuestionCreate(BaseModel):
    text: str
    is_scored: Optional[bool] = True

class QuizQuestionUpdate(BaseModel):
    text: Optional[str] = None
    is_scored: Optional[bool] = None

class QuizQuestionResponse(BaseModel):
    id: int
    text: str
    is_scored: bool

    model_config = {
        "from_attributes": True
    }