import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.auth_service import login
from models.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login")
def login_route(data: dict, db: Session = Depends(get_db)):
    logger.info("Login request received")
    advisor = login(db, data.get("email"), data.get("password"))
    if advisor:
        return {"message": "Login successful", "advisor": advisor}
    raise HTTPException(status_code=401, detail="Invalid email or password")

@router.post("/logout")
def logout_route():
    logger.info("Logout request received")
    return {"message": "Logout successful"}