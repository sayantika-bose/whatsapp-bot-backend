# app/models/config_models.py
from pydantic import BaseModel, Field, validator
import re

class ContentSIDsRequest(BaseModel):
    first_content_sid: str = Field(..., description="First content SID")
    
    @validator('first_content_sid')
    def validate_sid_format(cls, v):
        if not re.match(r'^HX[a-f0-9]{32}$', v):
            raise ValueError('SID must start with HX followed by 32 hex characters')
        return v

class ContentSIDsResponse(BaseModel):
    success: bool
    message: str
    first_content_sid: str | None = None

class ErrorResponse(BaseModel):
    detail: str