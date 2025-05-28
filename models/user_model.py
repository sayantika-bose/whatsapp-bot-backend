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
    salutation: Optional[str] = ""
    first_name: Optional[str]
    last_name: Optional[str] = ""
    email: Optional[EmailStr] = ""
    mobile_number: str
    age_group: Optional[str] = ""
    advisor_id: int # Is it NOT NULL in DB 
    recaptcha_token: Optional[str] = ""
    message: Optional[str] = ""  # Make the message field optional

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

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