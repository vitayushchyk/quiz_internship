from typing import List

from pydantic import BaseModel, field_validator

from poll.db.model_quiz import QuizStatus
from poll.services.exc.base_exc import (
    QuestionNoCorrectOptionError,
    QuizTooFewQuestionsError,
)


class BaseOptionData(BaseModel):
    text: str

    class Config:
        orm_mode = True


class OptionData(BaseOptionData):
    is_correct: bool


class PublicOptionData(BaseOptionData):
    pass


class BaseQuestionData(BaseModel):
    title: str
    options: List[BaseOptionData]


class QuestionData(BaseQuestionData):
    options: List[OptionData]

    @field_validator("options")
    def validate_options(cls, options):
        if len(options) < 2:
            raise QuizTooFewQuestionsError
        if not any(option.is_correct for option in options):
            raise QuestionNoCorrectOptionError
        return options


class PublicQuestionData(BaseQuestionData):
    options: List[PublicOptionData]


class BaseQuizRes(BaseModel):
    id: int
    title: str
    description: str
    company_id: int
    creator_id: int


class QuizRes(BaseQuizRes):
    questions: List[QuestionData]


class PublicQuizRes(BaseQuizRes):
    questions: List[PublicQuestionData]


class CreateQuizReq(BaseModel):
    title: str
    description: str
    questions_data: List[QuestionData]


class UpdateQuizReq(BaseModel):
    new_title: str


class UpdateQuizRes(BaseModel):
    id: int
    new_title: str


class QuizStatusRes(BaseModel):
    id: int
    company_id: int
    created_by: int
    title: str
    status: QuizStatus
    description: str


class AttemptAnswer(BaseModel):
    question_id: int
    option_id: int


class AttemptQuizRequest(BaseModel):
    quiz_id: int
    answers: List[AttemptAnswer]


class QuizResult(BaseModel):
    score: float
    correct_answers: int
    total_questions: int


class AverageScoreRes(BaseModel):
    average_score: float
