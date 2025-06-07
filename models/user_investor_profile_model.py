from typing import Optional, List

from pydantic import BaseModel, EmailStr
from datetime import datetime


class AnswerInput(BaseModel):
    question_id: int
    answer_id: int

class UserInput(BaseModel):
    name: str
    mobile_number: str
    advisor_id: Optional[int] = None
    email: Optional[EmailStr] = None
    salutation: Optional[str] = None
    age_group: Optional[str] = None

class CompleteQuizFlowRequest(BaseModel):
    session_id: int
    answers: List[AnswerInput]
    user: UserInput

class InvestorProfileBase(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }

class UserInvestorProfileResponse(BaseModel):
    id: int
    user_id: int
    profile_id: int
    percentage: float
    created_at: datetime
    profile: InvestorProfileBase

    model_config = {
        "from_attributes": True
    }