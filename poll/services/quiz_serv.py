from poll.db.model_company import CompanyRole
from poll.db.model_quiz import QuizStatus
from poll.schemas.quiz_shemas import (
    AttemptQuizRequest,
    AttemptQuizResult,
    CreateQuizRequest,
)
from poll.services.exc.base_exc import (
    InvalidAnswerError,
    PermissionDeniedError,
    QuizFoundError,
)


class QuizCRUD:
    def __init__(self, quiz_repo, company_repo, user_repo):
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
        quiz_data: CreateQuizRequest,
    ):

        await self._check_permissions(
            company_id, user_id, [CompanyRole.OWNER, CompanyRole.ADMIN]
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

    async def editing_quiz(
        self, quiz_id: int, user_id: int, title: str, description: str
    ):
        quiz = await self.quiz_repo.get_quiz(quiz_id)
        if not quiz:
            raise QuizFoundError(quiz_id=quiz_id)

        await self._check_permissions(
            quiz.company_id, user_id, [CompanyRole.OWNER, CompanyRole.ADMIN]
        )

        updated_quiz = await self.quiz_repo.update_quiz_fields(quiz, title, description)
        return updated_quiz

    async def adding_new_quiz_status(self, quiz_id: int, status: str, user_id: int):
        quiz = await self.quiz_repo.get_quiz(quiz_id)
        if not quiz:
            raise QuizFoundError(quiz_id=quiz_id)

        await self._check_permissions(
            quiz.company_id, user_id, [CompanyRole.OWNER, CompanyRole.ADMIN]
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
            quiz.company_id, user_id, [CompanyRole.OWNER, CompanyRole.ADMIN]
        )
        await self.quiz_repo.delete_quiz(quiz_id=quiz_id)
        return None

    async def take_quiz(self, user_id: int, data: AttemptQuizRequest):
        quiz = await self.quiz_repo.get_quiz(data.quiz_id)
        if not quiz:
            raise QuizFoundError(quiz_id=data.quiz_id)

        if len(data.answers) != len(quiz.questions):
            raise InvalidAnswerError()

        correct_questions = 0

        for user_answer in data.answers:

            question = next(
                (q for q in quiz.questions if q.id == user_answer.question_id), None
            )
            if not question:
                raise InvalidAnswerError()

            correct_option = next(
                (option for option in question.options if option.is_correct), None
            )

            if correct_option and user_answer.option_id == correct_option.id:
                correct_questions += 1

        total_questions = len(quiz.questions)
        score = (correct_questions / total_questions) * 100
        passed = correct_questions == total_questions

        await self.quiz_repo.save_quiz_attempt(
            quiz=data.quiz_id,
            user_id=user_id,
            correct_answer=correct_questions,
            total_questions=total_questions,
        )

        return AttemptQuizResult(
            score=score,
            correct_answers=correct_questions,
            total_questions=total_questions,
        )
