# app/services/config_service.py
from models.config_model import ContentSIDsRequest, ContentSIDsResponse
import os
from dotenv import load_dotenv, set_key
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

ENV_FILE_PATH = ".env"

class ConfigService:
    @staticmethod
    def _clean_value(value: str) -> str:
        """Remove single or double quotes from value"""
        return value.strip("'\"")

    @staticmethod
    def get_content_sids() -> ContentSIDsResponse:
        logger.info("Fetching content SIDs from .env")
        try:
            load_dotenv(ENV_FILE_PATH)
            first_sid = os.getenv("FIRST_CONTENT_SID")
            
            if not first_sid:
                raise HTTPException(
                    status_code=404,
                    detail="Content SIDs not found"
                )
            
            return ContentSIDsResponse(
                success=True,
                message="Content SIDs retrieved successfully",
                first_content_sid=first_sid
            )
        except Exception as e:
            logger.error(f"Error fetching content SIDs: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def update_content_sids(request: ContentSIDsRequest) -> ContentSIDsResponse:
        logger.info("Updating FIRST_CONTENT_SID and LAST_CONTENT_SID in .env")
        
        if not os.path.exists(ENV_FILE_PATH):
            logger.error(".env file not found")
            raise HTTPException(status_code=500, detail=".env file not found")
        
        try:
            clean_first_sid = ConfigService._clean_value(request.first_content_sid)
            
            set_key(ENV_FILE_PATH, "FIRST_CONTENT_SID", clean_first_sid, quote_mode="never")
            
            load_dotenv(ENV_FILE_PATH, override=True)
            
            return ContentSIDsResponse(
                success=True,
                message="Content SIDs updated successfully",
                first_content_sid=clean_first_sid
            )
        except Exception as e:
            logger.error(f"Error updating .env file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update .env file")