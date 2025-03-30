from pydantic import BaseModel, EmailStr, SecretStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    advisor: dict