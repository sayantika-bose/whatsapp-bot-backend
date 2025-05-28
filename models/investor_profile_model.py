from pydantic import BaseModel
from typing import Optional

class InvestorProfileCreate(BaseModel):
    name: str
    description: Optional[str] = None
    emoji: Optional[str] = None
    ponderation: Optional[int] = 1

class InvestorProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    emoji: Optional[str] = None
    ponderation: Optional[int] = None

class InvestorProfileResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    emoji: Optional[str]
    ponderation: int

    model_config = {
        "from_attributes": True
    }