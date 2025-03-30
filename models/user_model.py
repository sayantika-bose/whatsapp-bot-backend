from pydantic import BaseModel, EmailStr
from typing import List, Optional

class SubmitFormRequest(BaseModel):
    name: str
    email: EmailStr
    mobile_number: str
    message: str

class SubmitFormResponse(BaseModel):
    success: bool
    message: str

class UserResponse(BaseModel):
    id: int
    name: str
    mobile_number: str
    email: EmailStr
    advisor_id: int
    age_group: Optional[str]
    salutation: Optional[str]

    class Config:
        orm_mode = True

class UserRepliesResponse(BaseModel):
    replies: List[dict]