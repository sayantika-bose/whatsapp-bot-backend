import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.auth_service import login
from models.database import get_db
from models.auth_model import LoginRequest, LoginResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login")
def login_route(data: LoginRequest, db: Session = Depends(get_db)):
    logger.info("Login request received")
    advisor = login(db, data.email, data.password)  # Unwrap SecretStr here
    if advisor:
        return LoginResponse(message="Login successful", advisor=advisor)
    raise HTTPException(status_code=401, detail="Invalid email or password")

@router.post("/logout", response_model=LoginResponse)
def logout_route():
    logger.info("Logout request received")
    return LoginResponse(message="Logout successful", advisor=None)