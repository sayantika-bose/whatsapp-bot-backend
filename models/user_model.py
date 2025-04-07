from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class SubmitFormRequest(BaseModel):
    salutation: str
    first_name: str
    last_name: str
    email: EmailStr
    mobile_number: str
    age_group: str
    advisor_id: int
    recaptcha_token: str
    message: Optional[str] = None  # Make the message field optional

    @property
    def name(self):
        return f"{self.salutation} {self.first_name} {self.last_name}"

class SubmitFormResponse(BaseModel):
    success: bool
    message_sid: str
    message: str
    timestamp: str

class UserResponse(BaseModel):
    id: int
    salutation: str | None
    name: str
    mobile_number: str
    email: str | None
    advisor_id: int | None
    age_group: str | None
    created_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode

class UserRepliesResponse(BaseModel):
    id: int
    user_id: int
    question_id: int
    reply: str
    created_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode

class DeleteUserRequest(BaseModel):
    user_id: int
    advisor_id: int

class DeleteUserResponse(BaseModel):
    message: str
    user_id: int