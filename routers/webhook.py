import logging
from fastapi import FastAPI, Request, Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.messaging_service import handle_webhook
from models.database import get_db
from services.user_service import user_sessions
from models.webhook_model import WebhookResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/webhook")
async def webhook_endpoint(request: Request, db: AsyncSession = Depends(get_db)):

    response_data = await handle_webhook(db, request)

    return response_data