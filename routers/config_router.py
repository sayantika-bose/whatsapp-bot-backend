# app/routers/config_router.py
from fastapi import APIRouter, HTTPException
from services.config_service import ConfigService
from models.config_model import ContentSIDsRequest, ContentSIDsResponse, ErrorResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["config"])

@router.put(
    "/update-content-sids",
    response_model=ContentSIDsResponse,
    responses={500: {"model": ErrorResponse}}
)
async def update_content_sids(request: ContentSIDsRequest):
    try:
        return ConfigService.update_content_sids(request)
    except Exception as e:
        logger.error(f"Error in update_content_sids endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/content-sids",
    response_model=ContentSIDsResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_content_sids():
    try:
        return ConfigService.get_content_sids()
    except Exception as e:
        logger.error(f"Error in get_content_sids endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))