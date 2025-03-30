from pydantic import BaseModel, Field
from typing import List, Optional

# Request Models
class AddQuestionRequest(BaseModel):
    advisor_id: int = Field(..., description="ID of the advisor")
    question: str = Field(..., description="The question text")
    triggerKeyword: str = Field(..., description="Keyword that triggers the question")
    is_predefined_answer: Optional[bool] = Field(False, description="Indicates if the answer is predefined")

class UpdateQuestionRequest(BaseModel):
    step: int = Field(..., description="Step number of the question")
    question: str = Field(..., description="The updated question text")

# Response Models
class QuestionResponse(BaseModel):
    id: int
    step: int
    question: str
    triggerKeyword: str

class QuestionListResponse(BaseModel):
    questions: List[QuestionResponse]

class MessageResponse(BaseModel):
    message: str