import json
from datetime import timedelta

from redis.asyncio import Redis

from poll.db.model_company import CompanyRole
from poll.db.model_quiz import QuizStatus
from poll.schemas.quiz_shemas import (
    AttemptAnswer,
    AttemptQuizRequest,
    CreateQuizReq,
    QuizResult,
    TimePeriodEnum,
    UserRatingRes,
    UserTestRes,
)
from poll.services.exc.base_exc import (
    GeneralPermissionError,
    InvalidAnswerError,
    PermissionDeniedError,
    QuizFoundError,
    ResultNotFound,
)


class QuizCRUD:
    def __init__(
        self,
        quiz_repo,
        company_repo,
        user_repo,
    ):
        self.quiz_repo = quiz_repo
        self.company_repo = company_repo
        self.user_repo = user_repo

    async def _check_permissions(
        self, company_id: int, user_id: int, required_roles: list[str]
    ):
        get_user_role = await self.company_repo.get_user_role(company_id, user_id)
        if not get_user_role or get_user_role.role not in required_roles:
            raise PermissionDeniedError(required_roles=required_roles)

    async def create_quiz(
        self,
        company_id: int,
        user_id: int,
        quiz_data: CreateQuizReq,
    ):

        await self._check_permissions(
            company_id=company_id,
            user_id=user_id,
            required_roles=[CompanyRole.OWNER, CompanyRole.ADMIN],
        )

        quiz = await self.quiz_repo.add_quiz(
            company_id=company_id,
            user_id=user_id,
            title=quiz_data.title,
            description=quiz_data.description,
        )

        for question_data in quiz_data.questions_data:

            question = await self.quiz_repo.add_question(
                quiz_id=quiz.id, title=question_data.title
            )

            for option_data in question_data.options:
                await self.quiz_repo.add_question_option(
                    question_id=question.id,
                    option_text=option_data.text,
                    is_correct=option_data.is_correct,
                )

        return quiz

    async def editing_quiz_title(self, quiz_id: int, user_id: int, title: str):
        quiz = await self.quiz_repo.get_quiz(quiz_id)
        if not quiz:
            raise QuizFoundError(quiz_id=quiz_id)

        await self._check_permissions(
            company_id=quiz.company_id,
            user_id=user_id,
            required_roles=[CompanyRole.OWNER, CompanyRole.ADMIN],
        )

        updated_quiz = await self.quiz_repo.update_quiz_title(quiz=quiz, title=title)
        return updated_quiz

    async def adding_new_quiz_status(self, quiz_id: int, status: str, user_id: int):
        quiz = await self.quiz_repo.get_quiz(quiz_id)
        if not quiz:
            raise QuizFoundError(quiz_id=quiz_id)

        await self._check_permissions(
            company_id=quiz.company_id,
            user_id=user_id,
            required_roles=[CompanyRole.OWNER, CompanyRole.ADMIN],
        )
        updated_quiz = await self.quiz_repo.add_new_quiz_status(
            quiz=quiz, status=status
        )
        return updated_quiz

    async def all_quiz_by_status(
        self, status: QuizStatus, page: int = 1, page_size: int = 20
    ):
        return await self.quiz_repo.get_quizzes_by_status(
            status=status, page=page, page_size=page_size
        )

    async def delete_quiz(self, quiz_id: int, user_id: int):
        quiz = await self.quiz_repo.get_quiz(quiz_id)
        if not quiz:
            raise QuizFoundError(quiz_id=quiz_id)
        await self._check_permissions(
            company_id=quiz.company_id,
            user_id=user_id,
            required_roles=[CompanyRole.OWNER, CompanyRole.ADMIN],
        )
        await self.quiz_repo.delete_quiz(quiz_id=quiz_id)
        return None

    async def take_quiz(self, user_id: int, data: AttemptQuizRequest, redis: Redis):
        quiz = await self.quiz_repo.get_quiz(data.quiz_id)
        if not quiz:
            raise QuizFoundError(quiz_id=data.quiz_id)

        if len(data.answers) != len(quiz.questions):
            raise InvalidAnswerError()

        correct_questions = 0

        quiz_answers = []
        validated_answers = []

        for user_answer in data.answers:

            question = next(
                (q for q in quiz.questions if q.id == user_answer.question_id), None
            )
            if not question:
                raise InvalidAnswerError()

            correct_option = next(
                (option for option in question.options if option.is_correct), None
            )

            is_correct = correct_option and user_answer.option_id == correct_option.id
            if is_correct:
                correct_questions += 1

            quiz_answers.append(
                {
                    "question_id": user_answer.question_id,
                    "user_id": user_id,
                    "quiz_id": data.quiz_id,
                    "company_id": quiz.company_id,
                    "user_answer": user_answer.option_id,
                    "is_correct": is_correct,
                }
            )

            validated_answers.append(
                AttemptAnswer(
                    question_id=user_answer.question_id, option_id=user_answer.option_id
                )
            )

        total_questions = len(quiz.questions)
        score = (correct_questions / total_questions) * 100

        await self.quiz_repo.save_quiz_attempt(
            quiz=data.quiz_id,
            user_id=user_id,
            correct_answer=correct_questions,
            total_questions=total_questions,
        )
        await self.quiz_repo.update_last_attempt_time(
            user_id=user_id, quiz_id=data.quiz_id
        )

        redis_key = f"quiz:{data.quiz_id}:user:{user_id}"
        await redis.set(redis_key, json.dumps(quiz_answers), ex=timedelta(hours=48))

        return QuizResult(
            quiz_id=data.quiz_id,
            answers=validated_answers,
            score=score,
            correct_answers=correct_questions,
            total_questions=len(quiz.questions),
        )

    async def get_quiz_by_id(self, quiz_id: int):
        quiz = await self.quiz_repo.get_quiz(quiz_id)
        if not quiz:
            raise QuizFoundError(quiz_id=quiz_id)
        return quiz

    async def get_user_results(
        self, user_id: int, current_user: int, page: int = 1, page_size: int = 10
    ):
        if user_id != current_user:
            raise GeneralPermissionError
        return await self.quiz_repo.get_user_quiz_stats(
            user_id=user_id, page=page, page_size=page_size
        )

    async def get_company_results(
        self, company_id: int, user_id: int, page: int = 1, page_size: int = 10
    ):
        await self._check_permissions(
            company_id=company_id,
            user_id=user_id,
            required_roles=[CompanyRole.OWNER, CompanyRole.ADMIN],
        )
        get_stat = await self.quiz_repo.get_user_quiz_stats(
            user_id=user_id, company_id=company_id, page=page, page_size=page_size
        )
        if not get_stat:
            raise ResultNotFound()
        return get_stat

    async def get_user_results_in_company(
        self,
        company_id: int,
        user_id: int,
        current_user_id: int,
        page: int = 1,
        page_size: int = 10,
    ):

        await self._check_permissions(
            company_id=company_id,
            user_id=current_user_id,
            required_roles=[CompanyRole.OWNER, CompanyRole.ADMIN],
        )
        get_stat = await self.quiz_repo.get_user_quiz_stats(
            user_id=user_id, company_id=company_id, page=page, page_size=page_size
        )
        if not get_stat:
            raise ResultNotFound()
        return get_stat

    async def get_results_for_quiz(
        self,
        quiz_id: int,
        user_id: int,
        current_user: int,
        page: int = 1,
        page_size: int = 10,
    ):
        quiz = await self.quiz_repo.get_quiz(quiz_id)
        if quiz is None:
            raise QuizFoundError(quiz_id=quiz_id)
        if user_id != current_user:
            raise GeneralPermissionError

        return await self.quiz_repo.get_results_for_quiz(
            quiz_id=quiz_id, user_id=user_id, page=page, page_size=page_size
        )

    async def get_user_overall_rating(
        self, user_id: int, current_user: int, page: int = 1, page_size: int = 10
    ) -> UserRatingRes:
        if user_id != current_user:
            raise GeneralPermissionError

        overall_avg_score = await self.quiz_repo.get_avg_score(user_id=user_id)
        test_scores = await self.quiz_repo.get_user_test_scores(
            user_id=user_id, page=page, page_size=page_size
        )

        if not test_scores:
            raise ResultNotFound()

        return UserRatingRes(
            overall_average_score=overall_avg_score,
            tests=[
                UserTestRes(
                    quiz_id=test["quiz_id"],
                    quiz_title=test["quiz_title"],
                    average_score=test["average_score"],
                    attempts=test["attempts"],
                    last_attempt=test["last_attempt"].isoformat(),
                )
                for test in test_scores
            ],
        )

    async def get_avg_scores_in_time_period(
        self, company_id: int, admin_user_id: int, time_period: TimePeriodEnum
    ):

        await self._check_permissions(
            company_id=company_id,
            user_id=admin_user_id,
            required_roles=[CompanyRole.OWNER, CompanyRole.ADMIN],
        )
        results = await self.quiz_repo.get_avg_scores_company_users(
            company_id=company_id, time_period=time_period
        )
        if not results:
            raise ResultNotFound()

        return results

    async def get_company_users_last_attempt(
        self, company_id: int, user_id: int, page: int = 1, page_size: int = 10
    ):
        await self._check_permissions(
            company_id=company_id,
            user_id=user_id,
            required_roles=[CompanyRole.OWNER, CompanyRole.ADMIN],
        )
        last_attempt = await self.quiz_repo.get_users_last_quiz_attempts(
            company_id=company_id, page=page, page_size=page_size
        )
        if not last_attempt:
            raise ResultNotFound()
        return last_attempt

    async def get_last_attempts_for_all_users(self):
        return await self.quiz_repo.get_last_attempts_for_all_users()
