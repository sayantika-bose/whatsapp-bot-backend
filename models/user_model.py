from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

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
    question:str
    reply:str

    class Config:
        from_attributes = True  # Enable ORM mode