import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from services.user_service import submit_form, get_users, get_user_replies
from services.messaging_service import send_message
from models.database import get_db
from models.user_model import SubmitFormRequest, SubmitFormResponse, UserResponse, UserRepliesResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/submit_form", response_model=SubmitFormResponse)
def submit_form_route(data: SubmitFormRequest, db: Session = Depends(get_db)):
    logger.info("Submit form request received")
    if data.message:
        logger.info(f"Message provided: {data.message}")
    else:
        logger.info("No message provided in the request")
    result, error = submit_form(db, data.model_dump())  # Use model_dump instead of dict
    if error:
        raise HTTPException(status_code=400 if "reCAPTCHA" in error else 409, detail=error)
    return SubmitFormResponse(**result)

@router.get("/users/{advisor_id}", response_model=List[UserResponse])
def get_users_route(advisor_id: int, db: Session = Depends(get_db)):
    logger.info(f"Get users request for advisor_id: {advisor_id}")
    users = get_users(db, advisor_id)  # Fetch users from the database
    return [UserResponse.model_validate(u) for u in users]  # Use model_validate

@router.get("/users/{advisor_id}/replies/{user_id}", response_model=List[UserRepliesResponse])
def get_user_replies_route(advisor_id: int, user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Get user replies request for advisor_id: {advisor_id}, user_id: {user_id}")
    replies = get_user_replies(db, advisor_id, user_id)  # Fetch replies from the database
    return [UserRepliesResponse.model_validate(r) for r in replies]  # Use model_validate

@router.post("/send_message")
async def send_message_route(data: dict, db: Session = Depends(get_db)):
    logger.info("Send message request received")
    # Await the send_message function
    message_sids = await send_message(db, data["content_sid"], data["advisor_id"], data.get("user_ids", []))
    return {"message_sids": message_sids}