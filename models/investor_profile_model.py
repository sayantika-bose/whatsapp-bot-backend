from pydantic import BaseModel
from typing import Optional

class InvestorProfileCreate(BaseModel):
    name: str
    description: str
    emoji: Optional[str]
    ponderation: float = 1

class InvestorProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    emoji: Optional[str] = None
    ponderation: Optional[float] = None

class InvestorProfileResponse(BaseModel):
    id: int
    name: str
    description: str
    emoji: Optional[str]
    ponderation: float

    model_config = {
        "from_attributes": True
    }