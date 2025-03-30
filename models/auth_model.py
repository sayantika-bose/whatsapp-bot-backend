from pydantic import BaseModel, EmailStr, SecretStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr

class LoginResponse(BaseModel):
    message: str
    advisor: dict