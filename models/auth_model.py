from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenData(BaseModel):
    email: Optional[str] = None

class AdvisorResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    advisor: Optional[AdvisorResponse] = None

class RefreshRequest(BaseModel):
    refresh_token: str

# Update forward references using model_rebuild()
TokenResponse.model_rebuild()