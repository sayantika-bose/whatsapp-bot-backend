from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import DecisionTreeQuestion, UserReply, User
import json
import logging
import os
import asyncio
from fastapi import Request
from typing import List, Optional
from services.session_manager import session_manager  # Import session manager

logger = logging.getLogger(__name__)

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

async def handle_webhook(db: AsyncSession, request: Request) -> str:
    logger.info("Received webhook request")
    response = MessagingResponse()
    
    try:
        form_data = await request.form()
        logger.info(f"Received form data: {dict(form_data)}")
        
        incoming_msg = form_data.get("Body", "").strip().lower()
        from_number = form_data.get("From", "").replace("whatsapp:", "")
        
        logger.info(f"Processed webhook message from {from_number}: {incoming_msg}")
        
        user_data = session_manager.get_session(from_number)

        if not user_data:
            logger.warning(f"No session found for {from_number}")
            response.message("Please submit the form to start the session.")
            return str(response)

        advisor_id = user_data["advisor_id"]

        if user_data["current_step"] is None and incoming_msg == "start":
            try:
                session_manager.set_session(from_number, {**user_data, "current_step": 1})
                question = await get_question(db, advisor_id, 1)
                response.message(body=question.question if question else "No questions found.")
                logger.info(f"Started session for {from_number} with step 1")
                return str(response)
            except Exception as e:
                logger.error(f"Error starting session for {from_number}: {str(e)}")
                response.message("An error occurred while starting the session.")
                return str(response)
        elif user_data["current_step"]:
            current_step = user_data["current_step"]
            try:
                current_question = await get_question(db, advisor_id, current_step)
                
                if not current_question:
                    logger.warning(f"No question found for step {current_step}")
                    response.message("No questions found.")
                    return str(response)

                if current_question.is_predefined_answer:
                    if incoming_msg == current_question.triggerKeyword.lower():
                        next_step = current_step + 1
                        next_question = await get_question(db, advisor_id, next_step)
                        session_manager.set_session(from_number, {**user_data, "current_step": next_step})
                        response.message(body=next_question.question if next_question else "Thank you! You've completed all questions.")
                        logger.info(f"Advanced to step {next_step} for {from_number}")
                        if not next_question:
                            session_manager.clear_session(from_number)
                            logger.info(f"Session completed for {from_number}")
                    else:
                        response.message(f"Please respond with '{current_question.triggerKeyword}'.")
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
                        response.message(body=next_question.question if next_question else "Thank you! You've completed all questions.")
                        if not next_question:
                            session_manager.clear_session(from_number)
                            logger.info(f"Session completed for {from_number}")
                    except Exception as e:
                        logger.error(f"Error processing reply for {from_number}: {str(e)}")
                        await db.rollback()
                        response.message("An error occurred while processing your reply.")
            except Exception as e:
                logger.error(f"Error processing step {current_step} for {from_number}: {str(e)}")
                response.message("An error occurred while processing your response.")
        else:
            response.message("Invalid session state. Please start again.")
            logger.warning(f"Invalid session state for {from_number}")
        
        return str(response)
    except Exception as e:
        logger.error(f"Unexpected error in webhook handler: {str(e)}")
        response.message("An unexpected error occurred.")
        return str(response)

async def get_question(db: AsyncSession, advisor_id: int, step: int) -> Optional[DecisionTreeQuestion]:
    logger.debug(f"Fetching question for advisor_id: {advisor_id}, step: {step}")
    try:
        smt = select(DecisionTreeQuestion).where(
                DecisionTreeQuestion.advisor_id == advisor_id,
                DecisionTreeQuestion.step == step
            )
        result = await db.execute(smt)
        question = result.scalars().first()
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
        users_query = User.__table__.select().where(
            User.advisor_id == advisor_id,
            User.id.in_(user_ids)
        ) if user_ids else User.__table__.select().where(
            User.advisor_id == advisor_id
        )
        
        result = await db.execute(users_query)
        users = result.scalars().all()
        
        if not users:
            logger.warning(f"No users found for advisor_id: {advisor_id}")
            return message_sids

        async def send_twilio_message(user):
            try:
                from_number = os.getenv("TWILIO_PHONE_NUMBER")
                message_service_sid = os.getenv("MESSAGING_SERVICE_SID")
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

        message_sids = await asyncio.gather(*(send_twilio_message(user) for user in users if user))
        valid_sids = [sid for sid in message_sids if sid]
        logger.info(f"Successfully sent {len(valid_sids)} messages for advisor_id: {advisor_id}")
        return valid_sids
    except Exception as e:
        logger.error(f"Error in send_message for advisor_id: {advisor_id}: {str(e)}")
        return message_sids