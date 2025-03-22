import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.user_service import submit_form, get_users, get_user_replies
from services.messaging_service import send_message
from models.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/submit_form")
def submit_form_route(data: dict, db: Session = Depends(get_db)):
    logger.info("Submit form request received")
    result, error = submit_form(db, data)
    if error:
        raise HTTPException(status_code=400 if "reCAPTCHA" in error else 409, detail=error)
    return result

@router.get("/user/{advisor_id}")
def get_users_route(advisor_id: int, db: Session = Depends(get_db)):
    logger.info(f"Get users request for advisor_id: {advisor_id}")
    users = get_users(db, advisor_id)
    return [{"id": u.id, "name": u.name, "mobile_number": u.mobile_number, "email": u.email, "advisor_id": u.advisor_id, "age_group": u.age_group, "salutation": u.salutation} for u in users]

@router.get("/user/{advisor_id}/replies/{user_id}")
def get_user_replies_route(advisor_id: int, user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Get user replies request for advisor_id: {advisor_id}, user_id: {user_id}")
    return get_user_replies(db, advisor_id, user_id)

@router.post("/user/send_message")
def send_message_route(data: dict, db: Session = Depends(get_db)):
    logger.info("Send message request received")
    message_sids = send_message(db, data["content_sid"], data["advisor_id"], data.get("user_ids", []))
    return {"message_sids": message_sids}