from poll.db.model_company import CompanyRole
from poll.db.model_quiz import QuizStatus
from poll.services.exc.base_exc import PermissionDeniedError, QuizErrors, QuizFoundError


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
        title: str,
        description: str,
        questions_data: list[dict],
    ):

        await self._check_permissions(
            company_id, user_id, [CompanyRole.OWNER, CompanyRole.ADMIN]
        )
        if len(questions_data) < 2:
            raise QuizErrors
        quiz = await self.quiz_repo.add_quiz(
            company_id=company_id,
            user_id=user_id,
            title=title,
            description=description,
        )
        for question_data in questions_data:
            if "options" not in question_data or len(question_data["options"]) < 2:
                raise ValueError("Each question must have at least two answer options.")
            if not any(option["is_correct"] for option in question_data["options"]):
                raise ValueError(
                    f"Question '{question_data['title']}' must have at least one correct answer."
                )

            question = await self.quiz_repo.add_question(
                quiz.id, question_data["title"]
            )

            for option_data in question_data["options"]:
                await self.quiz_repo.add_question(
                    question_id=question.id,
                    option_text=option_data["text"],
                    is_correct=option_data["is_correct"],
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
