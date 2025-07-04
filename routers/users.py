import logging
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from utils.decrypt_field import user_to_response

from services.user_service import (
    create_user,
    delete_user,
    get_users,
    get_user_replies
)
from services.auth_service import get_current_advisor
from services.messaging_service import send_message
from models.database import get_db
from models.user_model import (
    DeleteUserRequest,
    DeleteUserResponse,
    UserCreate,
    UserResponse,
    UserRepliesResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=UserResponse)
def create(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_advisor = Depends(get_current_advisor)
    ):
    return create_user(db, user_data, current_advisor)

@router.get("/{advisor_id}", response_model=List[UserResponse])
def get_users_route(
    advisor_id: int,
    db: Session = Depends(get_db),
    current_advisor = Depends(get_current_advisor)
):
    logger.info(f"Get users request for advisor_id: {advisor_id} by {current_advisor.email}")
    users = get_users(db, advisor_id)
    is_admin = current_advisor.role == "admin"
    return [user_to_response(user, is_admin=is_admin) for user in users]

@router.get("/{advisor_id}/replies/{user_id}", response_model=List[UserRepliesResponse])
def get_user_replies_route(advisor_id: int, user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Get user replies request for advisor_id: {advisor_id}, user_id: {user_id}")
    replies = get_user_replies(db, advisor_id, user_id)
    return [UserRepliesResponse.model_validate(r) for r in replies]

@router.post("/send_message")
async def send_message_route(data: dict, db: Session = Depends(get_db)):
    logger.info("Send message request received")
    message_sids = await send_message(db, data["content_sid"], data["advisor_id"], data.get("user_ids", []))
    return {"message_sids": message_sids}

@router.delete("/delete_user", response_model=DeleteUserResponse)
def delete_user_route(payload: DeleteUserRequest, db: Session = Depends(get_db)):
    logger.info(f"Delete user request received: user_id={payload.user_id}, advisor_id={payload.advisor_id}")
    result, error = delete_user(db, payload.user_id, payload.advisor_id)
    if error:
        raise HTTPException(status_code=404 if error == "User not found" else 500, detail=error)
    return DeleteUserResponse(**result)