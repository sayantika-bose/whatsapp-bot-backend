from pydantic import BaseModel, EmailStr
from typing import Optional

from models.financial_advisor_model import FinancialAdvisorResponse

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenData(BaseModel):
    email: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    advisor: Optional[FinancialAdvisorResponse] = None

class RefreshRequest(BaseModel):
    refresh_token: str

# Update forward references using model_rebuild()
TokenResponse.model_rebuild()