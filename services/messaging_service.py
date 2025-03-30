from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import DecisionTreeQuestion, UserReply, User
import json
import logging
import os
import asyncio
from fastapi import Request, Response
from typing import List, Optional, Dict, Any
from services.session_manager import session_manager
import time
import aiohttp
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Constants for rate limiting
MAX_REQUESTS_PER_SECOND = 5  # Adjust based on Twilio's rate limits
REQUEST_WINDOW = 1.0  # seconds

# Rate limiter for Twilio requests
class RateLimiter:
    def __init__(self, max_requests: int, window: float):
        self.max_requests = max_requests
        self.window = window
        self.timestamps = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        async with self._lock:
            now = time.time()
            # Remove timestamps outside the window
            self.timestamps = [ts for ts in self.timestamps if now - ts <= self.window]
            
            if len(self.timestamps) >= self.max_requests:
                # Wait until we can make another request
                sleep_time = self.timestamps[0] + self.window - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    # Recalculate after sleeping
                    now = time.time()
                    self.timestamps = [ts for ts in self.timestamps if now - ts <= self.window]
            
            self.timestamps.append(now)

# Initialize Twilio client
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

# Initialize rate limiter
twilio_rate_limiter = RateLimiter(MAX_REQUESTS_PER_SECOND, REQUEST_WINDOW)

async def handle_webhook(db: AsyncSession, request: Request) -> Response:
    logger.info("Received webhook request")
    twiml_response = MessagingResponse()
    
    try:
        form_data = await request.form()
        logger.info(f"Received form data: {dict(form_data)}")
        
        incoming_msg = form_data.get("Body", "").strip().lower()
        from_number = form_data.get("From", "").replace("whatsapp:", "")
        
        logger.info(f"Processed webhook message from {from_number}: {incoming_msg}")
        
        # Use async context manager for session operations to ensure thread safety
        async with get_user_session(from_number) as user_data:
            if not user_data:
                logger.warning(f"No session found for {from_number}")
                twiml_response.message("Please submit the form to start the session.")
                return Response(content=str(twiml_response), media_type="application/xml")

            advisor_id = user_data["advisor_id"]

            if user_data["current_step"] is None and incoming_msg == "start":
                try:
                    session_manager.set_session(from_number, {**user_data, "current_step": 1})
                    question = await get_question(db, advisor_id, 1)
                    twiml_response.message(body=question.question if question else "No questions found.")
                    logger.info(f"Started session for {from_number} with step 1")
                    return Response(content=str(twiml_response), media_type="application/xml")
                except Exception as e:
                    logger.error(f"Error starting session for {from_number}: {str(e)}")
                    twiml_response.message("An error occurred while starting the session.")
                    return Response(content=str(twiml_response), media_type="application/xml")
            elif user_data["current_step"]:
                current_step = user_data["current_step"]
                try:
                    current_question = await get_question(db, advisor_id, current_step)
                    
                    if not current_question:
                        logger.warning(f"No question found for step {current_step}")
                        twiml_response.message("No questions found.")
                        return Response(content=str(twiml_response), media_type="application/xml")

                    if current_question.is_predefined_answer:
                        if incoming_msg == current_question.triggerKeyword.lower():
                            next_step = current_step + 1
                            next_question = await get_question(db, advisor_id, next_step)
                            session_manager.set_session(from_number, {**user_data, "current_step": next_step})
                            twiml_response.message(body=next_question.question if next_question else "Thank you! You've completed all questions.")
                            logger.info(f"Advanced to step {next_step} for {from_number}")
                            if not next_question:
                                session_manager.clear_session(from_number)
                                logger.info(f"Session completed for {from_number}")
                        else:
                            twiml_response.message(f"Please respond with '{current_question.triggerKeyword}'.")
                            logger.warning(f"Invalid response '{incoming_msg}' for predefined question from {from_number}")
                    else:
                        try:
                            new_reply = UserReply(user_id=user_data["id"], question_id=current_question.id, reply=incoming_msg)
                            db.add(new_reply)
                            await db.commit()
                            logger.info(f"Stored reply for question ID: {current_question.id} from {from_number}")
                            
                            next_step = current_step + 1
                            next_question = await get_question(db, advisor_id, next_step)
                            session_manager.set_session(from_number, {**user_data, "current_step": next_step})
                            twiml_response.message(body=next_question.question if next_question else "Thank you! You've completed all questions.")
                            if not next_question:
                                session_manager.clear_session(from_number)
                                logger.info(f"Session completed for {from_number}")
                        except Exception as e:
                            logger.error(f"Error processing reply for {from_number}: {str(e)}")
                            await db.rollback()
                            twiml_response.message("An error occurred while processing your reply.")
                except Exception as e:
                    logger.error(f"Error processing step {current_step} for {from_number}: {str(e)}")
                    twiml_response.message("An error occurred while processing your response.")
            else:
                twiml_response.message("Invalid session state. Please start again.")
                logger.warning(f"Invalid session state for {from_number}")
        
        return Response(content=str(twiml_response), media_type="application/xml")
    except Exception as e:
        logger.error(f"Unexpected error in webhook handler: {str(e)}")
        twiml_response.message("An unexpected error occurred.")
        return Response(content=str(twiml_response), media_type="application/xml")

@asynccontextmanager
async def get_user_session(from_number):
    """Context manager for safely accessing user session data"""
    try:
        user_data = session_manager.get_session(from_number)
        yield user_data
    except Exception as e:
        logger.error(f"Error accessing session for {from_number}: {str(e)}")
        yield None

async def get_question(db: AsyncSession, advisor_id: int, step: int) -> Optional[DecisionTreeQuestion]:
    logger.debug(f"Fetching question for advisor_id: {advisor_id}, step: {step}")
    try:
        stmt = select(DecisionTreeQuestion).where(
            DecisionTreeQuestion.advisor_id == advisor_id,
            DecisionTreeQuestion.step == step
        )
        # Use synchronous execution as in your original code
        result = db.execute(stmt)  # No await here
        question = result.scalars().first()
        logger.debug(f"Question found for advisor_id: {advisor_id}, step: {step}: {question}")
        if not question:
            logger.debug(f"No question found for advisor_id: {advisor_id}, step: {step}")
        return question
    except Exception as e:
        logger.error(f"Error fetching question for advisor_id: {advisor_id}, step: {step}: {str(e)}")
        return None

async def send_message(db: AsyncSession, content_sid: str, advisor_id: int, user_ids: Optional[List[int]] = None) -> List[str]:
    logger.info(f"Sending message to users for advisor_id: {advisor_id}")
    message_sids = []
    
    try:
        users_query = select(User).where(
            User.advisor_id == advisor_id,
            User.id.in_(user_ids) if user_ids else True
        )
        
        # Use synchronous execution as in your original code
        result = db.execute(users_query)  # No await here
        users = result.scalars().all()
        
        if not users:
            logger.warning(f"No users found for advisor_id: {advisor_id}")
            return message_sids

        async def send_twilio_message(user):
            try:
                # Apply rate limiting
                await twilio_rate_limiter.acquire()
                
                from_number = os.getenv("TWILIO_PHONE_NUMBER")
                message_service_sid = os.getenv("MESSAGING_SERVICE_SID")
                
                # Use asyncio.to_thread for non-blocking I/O operations
                message = await asyncio.to_thread(
                    client.messages.create,
                    content_sid=content_sid,
                    from_=f"whatsapp:{from_number}",
                    content_variables=json.dumps({"1": user.name}),
                    messaging_service_sid=message_service_sid,
                    to=f"whatsapp:{user.mobile_number}",
                )
                logger.info(f"Message sent to {user.mobile_number}, SID: {message.sid}")
                return message.sid
            except Exception as e:
                logger.error(f"Failed to send message to {user.mobile_number}: {str(e)}")
                return None

        # Process users in chunks to prevent overwhelming the system
        CHUNK_SIZE = 20
        all_sids = []
        
        for i in range(0, len(users), CHUNK_SIZE):
            user_chunk = users[i:i+CHUNK_SIZE]
            chunk_sids = await asyncio.gather(*(send_twilio_message(user) for user in user_chunk if user))
            all_sids.extend(chunk_sids)
            
            # Brief pause between chunks
            if i + CHUNK_SIZE < len(users):
                await asyncio.sleep(0.5)
        
        valid_sids = [sid for sid in all_sids if sid]
        logger.info(f"Successfully sent {len(valid_sids)} messages for advisor_id: {advisor_id}")
        return valid_sids
    except Exception as e:
        logger.error(f"Error in send_message for advisor_id: {advisor_id}: {str(e)}")
        return message_sids