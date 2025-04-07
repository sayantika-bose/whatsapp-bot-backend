from sqlalchemy.orm import Session
from models.database import User, UserReply, DecisionTreeQuestion
import requests
from twilio.rest import Client
import os
import json
import logging
from datetime import datetime, timezone  # Added for timestamp
from services.session_manager import session_manager  # Import session manager

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

def submit_form(db: Session, data: dict):
    """
    Submit user form, create user if new with a timestamp, send WhatsApp message, and update session.
    Returns tuple (success_response, error_message).
    """
    try:
        logger.info("Processing form submission")
        # Verify reCAPTCHA
        if not verify_recaptcha(data["recaptcha_token"]):
            logger.warning("Invalid reCAPTCHA token provided")
            return None, "Invalid reCAPTCHA"

        # Check for existing user
        logger.info(f"Checking for existing user with mobile: {data['mobile_number']}")
        existing_user = db.query(User).filter(
            User.mobile_number == data["mobile_number"],
            User.advisor_id == data["advisor_id"]
        ).first()

        if existing_user:
            logger.info(f"User already exists: {existing_user.mobile_number}")
            session_manager.set_session(data["mobile_number"], {
                "name": existing_user.name,
                "mobile_number": existing_user.mobile_number,
                "email": existing_user.email,
                "advisor_id": existing_user.advisor_id,
                "id": existing_user.id,
                "current_step": None,
                "created_at": existing_user.created_at.isoformat() if existing_user.created_at else None  # Include timestamp if available
            })
            return None, "User already exists"

        # Create new user with timestamp
        logger.info("Creating new user")
        current_time = datetime.now(timezone.utc)  # UTC timestamp
        new_user = User(
            salutation=data["salutation"],
            name=f"{data['salutation']} {data['first_name']} {data['last_name']}",
            mobile_number=data["mobile_number"],
            email=data["email"],
            advisor_id=data["advisor_id"],
            age_group=data["age_group"],
            created_at=current_time  # Add timestamp here
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"New user created with ID: {new_user.id} at {current_time.isoformat()}")

        # Update user session with timestamp
        session_manager.set_session(data["mobile_number"], {
            "name": new_user.name,
            "mobile_number": new_user.mobile_number,
            "email": new_user.email,
            "advisor_id": new_user.advisor_id,
            "id": new_user.id,
            "current_step": None,
            "created_at": new_user.created_at.isoformat()  # Include timestamp in session
        })

        # Send WhatsApp message
        if not client:
            logger.error("Twilio client not initialized, skipping WhatsApp message")
            return {"message": "User created, but message not sent", "created_at": new_user.created_at.isoformat()}, None

        content_sid = os.getenv("CONTENT_SID")
        from_number = os.getenv("TWILIO_PHONE_NUMBER")
        if not content_sid or not from_number:
            logger.error("Twilio configuration missing: content_sid or from_number not set")
            return {"message": "User created, but message not sent", "created_at": new_user.created_at.isoformat()}, None

        logger.info(f"Sending WhatsApp message to: {data['mobile_number']}")
        message = client.messages.create(
            content_sid=content_sid,
            from_=f"whatsapp:{from_number}",
            content_variables=json.dumps({"1": f"{data['salutation']} {data['first_name']}"}),
            to=f"whatsapp:{data['mobile_number']}",
        )
        logger.info(f"WhatsApp message sent with SID: {message.sid}")
        return {
            "success": True,
            "message_sid": message.sid,
            "message": "Thanks for filling out the form...",
            "timestamp": new_user.created_at.isoformat()  # Include timestamp in response
        }, None

    except KeyError as e:
        logger.error(f"Missing required field in form data: {str(e)}")
        return None, f"Missing required field: {str(e)}"
    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}")
        db.rollback()  # Roll back on error to avoid partial commits
        return None, "Internal server error"

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
