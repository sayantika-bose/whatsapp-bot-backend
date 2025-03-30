from pydantic import BaseModel, Field
from typing import Optional

class TwilioWhatsAppWebhookRequest(BaseModel):
    SmsMessageSid: str = Field(..., description="Unique identifier for the SMS message")
    NumMedia: int = Field(..., description="Number of media items attached to the message")
    ProfileName: str = Field(..., description="Sender's profile name")
    SmsSid: str = Field(..., description="Unique identifier for the SMS")
    WaId: str = Field(..., description="WhatsApp ID of the sender")
    SmsStatus: str = Field(..., description="Status of the message")
    Body: str = Field(..., description="Text body of the message")
    To: str = Field(..., description="Receiver's WhatsApp number")
    NumSegments: int = Field(..., description="Number of segments in the message")
    MessageSid: str = Field(..., description="Unique identifier for the message")
    AccountSid: str = Field(..., description="Twilio account SID")
    From_: str = Field(..., alias="From", description="Sender's WhatsApp number")
    ApiVersion: str = Field(..., description="Twilio API version used")

    class Config:
        populate_by_name = True

class WebhookResponse(BaseModel):
    status: str
    message: str