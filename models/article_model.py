from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class ArticleCreate(BaseModel):
    advisor_id: int
    title: str
    content: str
    image_base64: str

    @field_validator('content')
    @classmethod
    def validate_word_count(cls, v):
        word_count = len(v.split())
        if word_count > 1250:
            raise ValueError('Article is too long. Maximum allowed: 1250 words (approx. 5 min read).')
        return v


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_base64: Optional[str] = None

    @field_validator('content')
    @classmethod
    def validate_word_count(cls, v):
        if v:
            word_count = len(v.split())
            if word_count > 1250:
                raise ValueError('Article is too long. Maximum allowed: 1250 words (approx. 5 min read).')
        return v


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    image_base64: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }