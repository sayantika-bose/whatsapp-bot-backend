import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.session_manager import session_manager
from services.user_service import send_whatsapp_message, process_quiz_flow, create_user
from models.database import get_db
from models.user_model import (
    SubmitFormRequest,
    SubmitFormResponse,
    UserCreate, 
)

logger = logging.getLogger(__name__)
router = APIRouter()



@router.post("/submit_form", response_model=SubmitFormResponse)
def submit_form_route(data: SubmitFormRequest, db: Session = Depends(get_db)):
    logger.info(f"Submit form request received")

    if data.message:
        logger.info(f"Message provided: {data.message}")
    else:
        logger.info("No message provided in the request")

    if data.is_quiz:
        logger.info("Quiz flow detected, processing quiz submission")

        investor_profiles = process_quiz_flow(db, data)

        message_sid = send_whatsapp_message(data, investor_profiles=investor_profiles)
        return SubmitFormResponse(
            success=True,
            message_sid=message_sid,
            message="Thanks for completing the quiz!",
            timestamp=datetime.now(timezone.utc),
            investor_profiles=investor_profiles
        )

    logger.info("Standard form flow detected, processing form submission")

    try:
        user_data = UserCreate(**data.user.model_dump(exclude={"is_quiz", "answers"}))
        new_user = create_user(db, user_data)

        session_manager.set_session(data.user.mobile_number, {
            "name": new_user.name,
            "mobile_number": new_user.mobile_number,
            "email": new_user.email,
            "advisor_id": new_user.advisor_id,
            "id": new_user.id,
            "current_step": None,
            "created_at": new_user.created_at.isoformat()
        })

        message_sid = send_whatsapp_message(data)

        return SubmitFormResponse(
            success=True,
            message_sid=message_sid,
            message="Thanks for filling out the form...",
            timestamp=new_user.created_at,
            investor_profiles=None
        )

    except KeyError as e:
        logger.error(f"Missing required field in form data: {str(e)}")
        raise HTTPException(status_code=409, detail=f"Missing required field: {str(e)}")

    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")