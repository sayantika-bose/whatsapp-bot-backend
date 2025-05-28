from pydantic import BaseModel
from datetime import datetime

class InvestorProfileBase(BaseModel):
    id: int
    name: str

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