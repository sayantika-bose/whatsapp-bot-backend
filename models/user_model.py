from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from models.user_investor_profile_model import UserInvestorProfileResponse


class UserCreate(BaseModel):
    salutation: Optional[str] = ""
    first_name: str
    last_name: str
    mobile_number: str
    email: Optional[EmailStr] = None
    advisor_id: Optional[int] = 1
    age_group: Optional[str] = None
    session_id: Optional[int] = None
    message: Optional[str] = None

    @property
    def name(self):
        return f"{self.salutation} {self.first_name} {self.last_name}".strip()


class UserUpdate(BaseModel):
    salutation: Optional[str] = ""
    name: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[EmailStr] = None
    advisor_id: Optional[int] = None
    age_group: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    salutation: Optional[str] = ""
    name: str
    mobile_number: str
    email: Optional[EmailStr]
    advisor_id: Optional[int]
    age_group: Optional[str]
    created_at: datetime
    success: Optional[bool]
    message_sid: Optional[str]
    message: Optional[str]
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }
    session_id: int

class UserInput(BaseModel):
    first_name: str
    last_name: str
    mobile_number: str
    advisor_id: Optional[int] = None
    email: Optional[EmailStr] = None
    salutation: Optional[str] = ""
    age_group: Optional[str] = None

class AnswerInput(BaseModel):
    question_id: int
    answer_id: int

class SubmitFormRequest(BaseModel):
    # Quizz needs
    is_quiz: bool
    session_id: Optional[int] = None
    answers: List[AnswerInput]
    user: UserInput
    message: Optional[str] = None  # Make the message field optional
    salutation: Optional[str] = ""

    @property
    def name(self):
        return f"{self.salutation} {self.first_name} {self.last_name}"

class SubmitFormResponse(BaseModel):
    success: Optional[bool]
    message_sid: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime
    investor_profiles: Optional[List[UserInvestorProfileResponse]] = None

    model_config = {
        "from_attributes": True
    }

class UserRepliesResponse(BaseModel):
    question:str
    reply:str

    class Config:
        from_attributes = True  # Enable ORM mode