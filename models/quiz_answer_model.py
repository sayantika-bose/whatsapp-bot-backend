from pydantic import BaseModel
from typing import Optional
from enum import Enum

from models.investor_profile_model import InvestorProfileResponse

class AnswerLabel(str, Enum):
    a = 'A'
    b = 'B'
    c = 'C'
    d = 'D'

class QuizAnswerCreate(BaseModel):
    label: Optional[AnswerLabel] = None
    text: str
    question_id: int
    profile_id: int

class QuizAnswerUpdate(BaseModel):
    label: Optional[AnswerLabel] = None
    text: Optional[str] = None
    question_id: Optional[int] = None
    profile_id: Optional[int] = None

class QuizAnswerResponse(BaseModel):
    id: int
    label: Optional[AnswerLabel]
    text: str
    profile: InvestorProfileResponse

    model_config = {
        "from_attributes": True
    }