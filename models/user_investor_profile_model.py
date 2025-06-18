from typing import Optional

from pydantic import BaseModel
from datetime import datetime

class InvestorProfileBase(BaseModel):
    id: int
    name: str
    description: str
    emoji: Optional[str]
    ponderation: float

    model_config = {
        "from_attributes": True
    }

class UserInvestorProfileResponse(BaseModel):
    id: int
    user_id: int
    profile_id: int
    percentage: float
    created_at: datetime
    profile: InvestorProfileBase

    model_config = {
        "from_attributes": True
    }