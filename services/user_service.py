from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.database import User, UserReply, DecisionTreeQuestion, UserAnswer
import requests
from twilio.rest import Client
import os
import json
import logging
from datetime import datetime, timezone  # Added for timestamp

from models.user_answer_model import UserAnswerCreate, BulkUserAnswerCreate
from models.user_investor_profile_model import UserInvestorProfileResponse
from models.user_model import UserResponse, SubmitFormRequest, UserCreate
from services.session_manager import session_manager  # Import session manager
from services.user_answer_service import create_bulk_user_answers_service
from services.user_investor_profile_service import calculate_and_save_user_profile

# Configure logging
logger = logging.getLogger(__name__)

user_sessions = {}

# Twilio client initialization (moved outside functions for reuse)
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
try:
    client = Client(account_sid, auth_token)
    logger.info("Twilio client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Twilio client: {str(e)}")
    client = None  # Fallback, though you might want to handle this differently

def verify_recaptcha(token: str) -> bool:
    """
    Verify reCAPTCHA token with Google's API.
    Returns True if valid, False otherwise.
    """
    try:
        secret_key = os.getenv("CAPTCHA_SECRET_KEY")
        url = os.getenv("CAPTCHA_URL")
        if not secret_key or not url:
            logger.error("reCAPTCHA configuration missing: secret_key or url not set")
            return False

        logger.info("Verifying reCAPTCHA token")
        payload = {'secret': secret_key, 'response': token}
        response = requests.post(url, data=payload, timeout=5)
        response.raise_for_status()
        result = response.json().get("success", False)
        logger.info(f"reCAPTCHA verification result: {result}")
        return result
    except requests.RequestException as e:
        logger.error(f"reCAPTCHA verification failed due to network error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in reCAPTCHA verification: {str(e)}")
        return False

def create_user(db: Session, user_data: UserCreate) -> UserResponse:
    # Check for uniqueness
    if db.query(User).filter(User.mobile_number == user_data.mobile_number).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mobile number already registered.")
    if user_data.email and db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    # Create user
    user = User(
        advisor_id=user_data.advisor_id,
        name=f"{user_data.salutation} {user_data.first_name} {user_data.last_name}",
        mobile_number=user_data.mobile_number,
        email=user_data.email,
        salutation=user_data.salutation,
        age_group=user_data.age_group,
        created_at=datetime.now(timezone.utc)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"New user created with ID: {user.id} at {datetime.now(timezone.utc)}")

    # Link answers to the user if session_id is provided
    if user_data.session_id:
        answers = db.query(UserAnswer).filter(UserAnswer.session_id == user_data.session_id).all()
        for ans in answers:
            ans.user_id = user.id
            ans.session_id = None  # Optional cleanup
        db.commit()

    return user

def process_quiz_flow(db: Session, data: SubmitFormRequest) -> List[UserInvestorProfileResponse]:
    transformed_answers = [
        UserAnswerCreate(question_id=a.question_id, answer_id=a.answer_id)
        for a in data.answers
    ]

    user_answers_payload = BulkUserAnswerCreate(
        session_id=data.session_id,
        answers=transformed_answers,
        user_id=None
    )
    create_bulk_user_answers_service(db, user_answers_payload)

    user_data = UserCreate(**data.user.model_dump(
        exclude={"is_quiz", "answers"}),
        session_id=data.session_id,
    )
    user = create_user(db, user_data)

    user_investors_profiles: list[UserInvestorProfileResponse] = calculate_and_save_user_profile(db, user.id)

    return user_investors_profiles

def send_whatsapp_message(data: SubmitFormRequest):
    if not client:
        logger.error("Twilio client not initialized, skipping WhatsApp message")
        return None

    content_sid = os.getenv("FIRST_CONTENT_SID")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")
    if not content_sid or not from_number:
        logger.error("Twilio configuration missing: content_sid or from_number not set")
        return None

    logger.info(f"Sending WhatsApp message to: {data.mobile_number}")
    message = client.messages.create(
        content_sid=content_sid,
        from_=f"whatsapp:{from_number}",
        content_variables=json.dumps({"1": f"{data.salutation} {data.first_name}"}),
        to=f"whatsapp:{data.mobile_number}",
    )
    logger.info(f"WhatsApp message sent with SID: {message.sid}")
    return message.sid

def get_users(db: Session, advisor_id: int):
    """
    Retrieve all users for a given advisor.
    """
    try:
        logger.info(f"Fetching users for advisor_id: {advisor_id}")
        users = db.query(User).filter_by(advisor_id=advisor_id).all()
        logger.info(f"Found {len(users)} users for advisor_id: {advisor_id}")
        return users  # `created_at` will be included in each User object if accessed
    except Exception as e:
        logger.error(f"Error fetching users for advisor_id {advisor_id}: {str(e)}")
        return []

def get_user_replies(db: Session, advisor_id: int, user_id: int):
    """
    Retrieve user replies joined with decision tree questions for a given advisor and user.
    """
    try:
        logger.info(f"Fetching replies for user_id: {user_id}, advisor_id: {advisor_id}")
        replies = db.query(UserReply).join(DecisionTreeQuestion).filter(
            UserReply.user_id == user_id,
            DecisionTreeQuestion.advisor_id == advisor_id
        ).all()
        replies_dict = {reply.question_id: reply.reply for reply in replies}

        questions = db.query(DecisionTreeQuestion).filter_by(advisor_id=advisor_id).all()
        result = [{"question": q.question, "reply": replies_dict[q.id]}
                  for q in questions if q.id in replies_dict]

        logger.info(f"Found {len(result)} replies for user_id: {user_id}")
        return result
    except Exception as e:
        logger.error(f"Error fetching replies for user_id {user_id}, advisor_id {advisor_id}: {str(e)}")
        return []