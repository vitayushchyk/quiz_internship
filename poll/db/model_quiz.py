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
    desc,
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

    async def update_quiz_title(
        self,
        quiz: Quiz,
        title: str,
    ) -> Quiz:
        logger.info(f"Updating quiz id={quiz.id}. New Title: {title}")

        quiz.title = title
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
            attempted_at=datetime.datetime.utcnow(),
        )
        self.session.add(quiz_statist)
        await self.session.commit()
        await self.session.refresh(quiz_statist)
        return quiz_statist

    async def update_last_attempt_time(self, user_id: int, quiz_id: int):
        logger.info(
            f"Updating last attempt time for user_id={user_id}, quiz_id={quiz_id}"
        )
        query = select(QuizStat).where(
            QuizStat.quiz_id == quiz_id, QuizStat.user_id == user_id
        )
        result = await self.session.execute(query)
        stat = result.scalar()
        if stat:
            stat.attempted_at = datetime.datetime.utcnow()
            await self.session.commit()

    async def get_avg_score(
        self, user_id: int, company_id: Optional[int] = None
    ) -> float:
        logger.info(
            f"Calculating average score for user_id={user_id}, company_id={company_id}"
        )
        query = select(func.avg(QuizStat.score)).where(QuizStat.user_id == user_id)
        if company_id:
            query = query.join(Quiz, QuizStat.quiz_id == Quiz.id).where(
                Quiz.company_id == company_id
            )

        result = await self.session.execute(query)
        avg_score = result.scalar()
        return avg_score if avg_score else 0.0

    async def get_system_avg_score(self) -> float:
        logger.info("Calculating system-wide average score")
        query = select(func.avg(QuizStat.score))
        result = await self.session.execute(query)
        avg_score = result.scalar()
        return avg_score if avg_score else 0.0

    async def get_user_quiz_stats(
        self,
        user_id: int,
        company_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ):
        logger.info(
            f"Fetching quiz stats for user_id={user_id}, company_id={company_id}. Page: {page}, Page Size: {page_size}"
        )
        query = select(QuizStat).where(QuizStat.user_id == user_id)
        if company_id:
            query = query.join(Quiz, QuizStat.quiz_id == Quiz.id).where(
                Quiz.company_id == company_id
            )
        pagination = Pagination(self.session, query, page, page_size)
        return await pagination.fetch_results()

    async def get_results_for_quiz(
        self, quiz_id: int, user_id: int = None, page: int = 1, page_size: int = 10
    ):
        query = select(QuizStat).where(QuizStat.quiz_id == quiz_id)
        if user_id:
            query = query.where(QuizStat.user_id == user_id)

        query = query.limit(page_size).offset((page - 1) * page_size)

        results = await self.session.execute(query)
        return [
            {
                "user_id": result.user_id,
                "score": result.score,
                "attempts": result.total_questions,
                "completed_at": result.attempted_at.isoformat(),
            }
            for result in results.scalars()
        ]

    async def get_user_test_scores(
        self, user_id: int, page: int = 1, page_size: int = 10
    ):
        logger.info(
            f"Fetching user test scores for user_id={user_id}, page={page}, page_size={page_size}."
        )
        query = (
            select(
                Quiz.id.label("quiz_id"),
                Quiz.title.label("quiz_title"),
                func.avg(QuizStat.score).label("average_score"),
                func.count(QuizStat.id).label("attempts"),
                func.max(QuizStat.attempted_at).label("last_attempt"),
            )
            .join(QuizStat, QuizStat.quiz_id == Quiz.id)
            .where(QuizStat.user_id == user_id)
            .group_by(Quiz.id, Quiz.title)
            .order_by(desc(func.max(QuizStat.attempted_at)))
        )
        query = query.limit(page_size).offset((page - 1) * page_size)

        results = await self.session.execute(query)

        return results.mappings().all()

    async def get_avg_scores_company_users(
        self, company_id: int, time_period: str
    ) -> list[dict]:
        logger.info(
            f"Fetching average scores for users in company_id={company_id} with time_period={time_period}"
        )

        query = (
            select(
                QuizStat.user_id,
                func.avg(QuizStat.score).label("average_score"),
                func.count(QuizStat.id).label("attempts"),
            )
            .join(Quiz, Quiz.id == QuizStat.quiz_id)
            .where(Quiz.company_id == company_id)
        )

        if time_period:
            query = query.add_columns(
                func.date_trunc(time_period, QuizStat.attempted_at).label("time_period")
            ).group_by(QuizStat.user_id, "time_period")
            query = query.order_by("time_period")
        else:
            query = query.group_by(QuizStat.user_id)

        result = await self.session.execute(query)
        rows = result.fetchall()

        return [
            {
                "user_id": row.user_id,
                "average_score": row.average_score,
                "attempts": row.attempts,
                "time_period": getattr(row, "time_period", None),
            }
            for row in rows
        ]

    async def get_users_last_quiz_attempts(
        self, company_id: int, page: int = 1, page_size: int = 10
    ):
        logger.info(
            f"Fetching last quiz attempts for users in company_id={company_id}, page={page}, page_size={page_size}"
        )

        query = (
            select(
                QuizStat.user_id, func.max(QuizStat.attempted_at).label("last_attempt")
            )
            .join(Quiz, Quiz.id == QuizStat.quiz_id)
            .where(Quiz.company_id == company_id)
            .group_by(QuizStat.user_id)
        )
        query = query.limit(page_size).offset((page - 1) * page_size)

        result = await self.session.execute(query)
        return [
            {"user_id": row.user_id, "last_attempt": row.last_attempt} for row in result
        ]

    async def get_last_attempts_for_all_users(self):
        logger.info("Fetching last attempts for all users")
        query = select(
            QuizStat.user_id,
            QuizStat.quiz_id,
            func.max(QuizStat.attempted_at).label("last_attempt"),
        ).group_by(QuizStat.user_id, QuizStat.quiz_id)
        result = await self.session.execute(query)
        return result.fetchall()
