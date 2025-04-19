import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from services.user_service import submit_form
from models.database import get_db
from models.user_model import (
    SubmitFormRequest,
    SubmitFormResponse, 
)

logger = logging.getLogger(__name__)
router = APIRouter()



@router.post("/submit_form", response_model=SubmitFormResponse)
def submit_form_route(data: SubmitFormRequest, db: Session = Depends(get_db)):
    logger.info("Submit form request received")
    if data.message:
        logger.info(f"Message provided: {data.message}")
    else:
        logger.info("No message provided in the request")
    result, error = submit_form(db, data.model_dump())
    if error:
        raise HTTPException(status_code=400 if "reCAPTCHA" in error else 409, detail=error)
    return SubmitFormResponse(**result)