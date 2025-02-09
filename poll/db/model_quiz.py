import datetime
from enum import Enum
from typing import Any, Optional, Sequence

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, relationship, selectinload

from poll.db.connection import Base
from poll.db.model_company import logger
from poll.services.pagination import Pagination


class QuizStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Quiz(Base):
    __tablename__ = "quizzes"

    id: int = Column(Integer, primary_key=True, nullable=False)
    company_id: int = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    created_by: int = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    title: str = Column(String(255), nullable=False)
    description: str = Column(String(500), nullable=False)
    status: QuizStatus = Column(
        ENUM(QuizStatus, name="quiz_status"), default=QuizStatus.DRAFT, nullable=False
    )

    stats: Mapped[list["QuizStat"]] = relationship(
        "QuizStat", back_populates="quiz", cascade="all, delete-orphan"
    )

    created_at: datetime.datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime.datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    company = relationship("Company", back_populates="quizzes")
    created_by_user = relationship("User")
    questions = relationship(
        "Question", back_populates="quiz", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("company_id", "title", name="uq_company_quiz_title"),
    )


class Question(Base):
    __tablename__ = "questions"

    id: int = Column(Integer, primary_key=True, nullable=False)
    quiz_id: int = Column(
        Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    title: str = Column(String(500), nullable=False)
    created_at: datetime.datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime.datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    quiz = relationship("Quiz", back_populates="questions")
    options = relationship(
        "QuestionOption", back_populates="question", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("quiz_id", "title", name="uq_quiz_question_title"),
    )


class QuestionOption(Base):
    __tablename__ = "question_options"

    id: int = Column(Integer, primary_key=True, nullable=False)
    question_id: int = Column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    option_text: str = Column(String(500), nullable=False)
    is_correct: bool = Column(Boolean, default=False, nullable=False)
    created_at: datetime.datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    question = relationship("Question", back_populates="options")


class QuizStat(Base):
    __tablename__ = "quiz_stats"

    id: int = Column(Integer, primary_key=True, nullable=False)
    quiz_id: int = Column(
        Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    user_id: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    attempted_at: datetime.datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    correct_answers: int = Column(Integer, default=0, nullable=False)
    total_questions: int = Column(Integer, default=0, nullable=False)
    score: float = Column(Float, default=0.0, nullable=False)

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="stats")
    user = relationship("User", back_populates="quiz_stats")


class QuizRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_quiz(
        self,
        company_id: int,
        user_id: int,
        title: str,
        description: Optional[str] = None,
    ) -> Quiz:
        logger.info(
            f"Adding a new quiz for company_id={company_id} by user_id={user_id}. Title: {title}"
        )

        new_quiz = Quiz(
            company_id=company_id,
            created_by=user_id,
            title=title,
            description=description,
            status=QuizStatus.DRAFT,
        )
        self.session.add(new_quiz)
        await self.session.commit()
        await self.session.refresh(new_quiz)
        return new_quiz

    async def add_question(self, quiz_id: int, title: str) -> Question:
        logger.info(f"Adding a new question to quiz_id={quiz_id}. Title: '{title}'")

        new_question = Question(
            quiz_id=quiz_id,
            title=title,
        )
        self.session.add(new_question)
        await self.session.commit()
        await self.session.refresh(new_question)
        return new_question

    async def add_question_option(
        self, question_id: int, option_text: str, is_correct: bool = False
    ) -> QuestionOption:
        logger.info(
            f"Adding a new option to question_id={question_id}. Option Text: '{option_text}', Is Correct: {is_correct}"
        )

        new_question_option = QuestionOption(
            question_id=question_id, option_text=option_text, is_correct=is_correct
        )
        self.session.add(new_question_option)

        await self.session.commit()

        await self.session.refresh(new_question_option)

        return new_question_option

    async def get_quiz(self, quiz_id: int) -> Quiz:
        logger.info(f"Fetching quiz by ID: {quiz_id}")
        query = (
            select(Quiz)
            .options(selectinload(Quiz.questions).selectinload(Question.options))
            .where(Quiz.id == quiz_id)
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def update_quiz_fields(
        self, quiz: Quiz, title: str, description: str
    ) -> Quiz:
        logger.info(
            f"Updating quiz id={quiz.id}. New Title: {title}, New Description: {description}"
        )

        quiz.title = title
        quiz.description = description
        await self.session.commit()
        await self.session.refresh(quiz)
        return quiz

    async def add_new_quiz_status(
        self,
        quiz: Quiz,
        status: QuizStatus,
    ) -> Quiz:
        logger.info(f"Updating status of quiz id={quiz.id} to {status}")

        quiz.status = status
        await self.session.commit()
        await self.session.refresh(quiz)

        return quiz

    async def get_quizzes_by_status(
        self, status: QuizStatus, page: int = 1, page_size: int = 20
    ) -> Sequence[Any]:
        logger.info(
            f"Fetching quizzes with status={status}. Page: {page}, Page Size: {page_size}"
        )

        query = (
            select(Quiz)
            .options(selectinload(Quiz.questions))
            .where(Quiz.status == status)
        )
        pagination = Pagination(self.session, query, page, page_size)
        return await pagination.fetch_results()

    async def delete_quiz(self, quiz_id: int) -> None:
        logger.info(f"Deleting quiz {quiz_id}")
        result = await self.session.execute(select(Quiz).where(Quiz.id == quiz_id))
        quiz = result.scalar()
        if quiz:
            await self.session.delete(quiz)
            await self.session.commit()
        return None

    async def save_quiz_attempt(
        self, quiz: int, user_id: int, correct_answer: int, total_questions: int
    ):
        logger.info(
            f"Saving quiz attempt for quiz={quiz}, user_id={user_id}, correct_answer={correct_answer}, total_questions={total_questions},"
        )
        score = correct_answer / total_questions if total_questions > 0 else 0
        quiz_statist = QuizStat(
            quiz_id=quiz,
            user_id=user_id,
            correct_answers=correct_answer,
            total_questions=total_questions,
            score=score,
        )
        self.session.add(quiz_statist)
        await self.session.commit()
        await self.session.refresh(quiz_statist)
        return quiz_statist

    async def get_correct_answers(self, question_id: int):
        query = select(QuestionOption).where(
            QuestionOption.question_id == question_id, QuestionOption.is_correct == True
        )
        result = await self.session.execute(query)
        return result.scalars().all()
