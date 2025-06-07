from pydantic import BaseModel, model_validator
from typing import Optional, List

from models.enums import AnswerLabel
from models.investor_profile_model import InvestorProfileResponse


class QuizAnswerCreate(BaseModel):
    label: Optional[AnswerLabel] = None
    text: str
    profile_id: int

class QuizAnswerBatchCreate(BaseModel):
    answers: List[QuizAnswerCreate]

    @model_validator(mode="after")
    def validate_answers(self, values):
        answers = values.get("answers")
        if len(answers) != 4:
            raise ValueError("Exactly 4 answers must be provided.")

        labels = [answer.label for answer in answers]
        expected_labels = {AnswerLabel.a, AnswerLabel.b, AnswerLabel.c, AnswerLabel.d}

        if set(labels) != expected_labels:
            raise ValueError("Labels must include exactly one of each: a, b, c, d.")

        return values

class QuizAnswerUpdate(BaseModel):
    label: Optional[AnswerLabel] = None
    text: Optional[str] = None
    profile_id: Optional[int] = None

class QuizAnswerResponse(BaseModel):
    id: int
    label: Optional[AnswerLabel]
    text: str
    profile: InvestorProfileResponse

    model_config = {
        "from_attributes": True
    }