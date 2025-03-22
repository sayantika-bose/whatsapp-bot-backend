import logging
from fastapi import FastAPI, Request, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from services.messaging_service import handle_webhook
from models.database import get_db
from services.user_service import user_sessions


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/webhook")
async def webhook_endpoint(request: Request, db: AsyncSession = Depends(get_db)):
    return await handle_webhook(db, request, user_sessions)