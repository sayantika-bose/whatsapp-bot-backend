import logging
from fastapi import FastAPI, Request, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from services.messaging_service import handle_webhook
from models.database import get_db
from services.user_service import user_sessions
from models.webhook_model import WebhookRequest, WebhookResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/webhook", response_model=WebhookResponse)
async def webhook_endpoint(request: WebhookRequest, db: AsyncSession = Depends(get_db)):
    logger.info("Webhook request received")
    response_data = await handle_webhook(db, request.dict(), user_sessions)
    return WebhookResponse(**response_data)