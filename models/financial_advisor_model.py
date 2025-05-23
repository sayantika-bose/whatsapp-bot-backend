from pydantic import BaseModel, EmailStr
from typing import Optional

class FinancialAdvisorCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class FinancialAdvisorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class FinancialAdvisorResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }