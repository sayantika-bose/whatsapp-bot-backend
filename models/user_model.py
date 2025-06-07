from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    salutation: Optional[str] = None
    name: str
    mobile_number: str
    email: Optional[EmailStr] = None
    advisor_id: Optional[int] = None
    age_group: Optional[str] = None
    session_id: Optional[int] = None

class UserUpdate(BaseModel):
    salutation: Optional[str] = None
    name: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[EmailStr] = None
    advisor_id: Optional[int] = None
    age_group: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    salutation: Optional[str]
    name: str
    mobile_number: str
    email: Optional[EmailStr]
    advisor_id: Optional[int]
    age_group: Optional[str]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

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

class UserRepliesResponse(BaseModel):
    question:str
    reply:str

    class Config:
        from_attributes = True  # Enable ORM mode