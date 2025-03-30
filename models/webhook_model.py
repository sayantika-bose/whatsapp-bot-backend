from pydantic import BaseModel
from typing import Dict, Any

class WebhookRequest(BaseModel):
    event_type: str
    payload: Dict[str, Any]

class WebhookResponse(BaseModel):
    status: str
    message: str