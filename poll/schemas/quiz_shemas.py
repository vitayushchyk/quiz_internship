from typing import List

from pydantic import BaseModel, field_validator

from poll.db.model_quiz import QuizStatus
from poll.services.exc.base_exc import (
    QuestionNoCorrectOptionError,
    QuizTooFewQuestionsError,
)


class OptionData(BaseModel):
    text: str
    is_correct: bool

    class Config:
        orm_mode = True


class QuestionData(BaseModel):
    title: str
    options: List[OptionData]

    @field_validator("options")
    def validate_options(cls, options):
        if len(options) < 2:
            raise QuizTooFewQuestionsError
        if not any(option.is_correct for option in options):
            raise QuestionNoCorrectOptionError
        return options


class CreateQuizRequest(BaseModel):
    title: str
    description: str
    questions_data: list[QuestionData]


class QuizRes(BaseModel):
    id: int
    title: str
    description: str
    questions: list[QuestionData]
    company_id: int
    creator_id: int

    class Config:
        orm_mode = True


class QuizStatusRes(BaseModel):
    id: int
    company_id: int
    created_by: int
    title: str
    status: QuizStatus
    description: str
