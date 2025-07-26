from pydantic import BaseModel, EmailStr
from typing import Optional

from models.enums import UserRoleEnum

class FinancialAdvisorCreate(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[UserRoleEnum] = UserRoleEnum.DEV

class FinancialAdvisorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRoleEnum] = UserRoleEnum.DEV

class FinancialAdvisorResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRoleEnum

    model_config = {
        "from_attributes": True
    }