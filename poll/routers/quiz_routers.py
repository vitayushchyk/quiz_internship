from typing import List

from fastapi import APIRouter, Depends, status

from poll.core.deps import get_current_user, get_current_user_id, get_quiz_crud
from poll.db.model_quiz import QuizStatus
from poll.db.model_users import User
from poll.schemas.quiz_shemas import (
    AttemptQuizRequest,
    AttemptQuizResult,
    CreateQuizRequest,
    QuizRes,
    QuizStatusRes,
)
from poll.services.exc.base_exc import QuizFoundError
from poll.services.quiz_serv import QuizCRUD

quiz_router = APIRouter(prefix="/quiz", tags=["Quiz"])


@quiz_router.post(
    "/create_quiz/", status_code=status.HTTP_201_CREATED, response_model=QuizRes
)
async def create_quiz(
    company_id: int,
    data: CreateQuizRequest,
    current_user_id: int = Depends(get_current_user_id),
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
):
    quiz = await quiz_crud.create_quiz(
        company_id=company_id,
        user_id=current_user_id,
        quiz_data=data,
    )
    return QuizRes(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        questions=data.questions_data,
        company_id=quiz.company_id,
        creator_id=quiz.created_by,
    )


@quiz_router.put(
    "/{quiz_id}/",
    response_model=QuizRes,
    description="`Owner/Admin` create quiz",
    status_code=status.HTTP_200_OK,
)
async def edit_quiz(
    quiz_id: int,
    data: CreateQuizRequest,
    current_user_id: int = Depends(get_current_user_id),
    quiz_service: "QuizCRUD" = Depends(get_quiz_crud),
):
    try:
        quiz = await quiz_service.editing_quiz(
            quiz_id=quiz_id,
            user_id=current_user_id,
            title=data.title,
            description=data.description,
        )
        return QuizRes(
            id=quiz.id,
            title=quiz.title,
            description=quiz.description,
            company_id=quiz.company_id,
            creator_id=quiz.created_by,
        )
    except QuizFoundError:
        raise QuizFoundError(quiz_id=quiz_id)


@quiz_router.put(
    "/{quiz_id}/change-status/",
    response_model=QuizStatusRes,
    description="`Owner/Admin` update quiz",
    status_code=status.HTTP_200_OK,
)
async def update_quiz_status(
    quiz_id: int,
    status_data: QuizStatus,
    current_user_id: int = Depends(get_current_user_id),
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
):
    updated_quiz = await quiz_crud.adding_new_quiz_status(
        quiz_id=quiz_id, user_id=current_user_id, status=status_data
    )
    return QuizStatusRes(
        id=updated_quiz.id,
        company_id=updated_quiz.company_id,
        created_by=updated_quiz.created_by,
        title=updated_quiz.title,
        status=updated_quiz.status,
        description=updated_quiz.description,
    )


@quiz_router.post(
    "/",
    response_model=List[QuizStatusRes],
    description="`Owner/Admin` can change quiz status ",
    status_code=status.HTTP_200_OK,
)
async def get_quizzes_by_status(
    status: QuizStatus,
    page: int = 1,
    page_size: int = 1,
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
):
    quizzes = await quiz_crud.all_quiz_by_status(status, page=page, page_size=page_size)
    return [
        QuizStatusRes(
            id=quiz.id,
            company_id=quiz.company_id,
            created_by=quiz.created_by,
            title=quiz.title,
            status=quiz.status,
            description=quiz.description,
        )
        for quiz in quizzes
    ]


@quiz_router.delete(
    "/{quiz_id}",
    description="`Owner/Admin` delete quiz",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_quiz(
    quiz_id: int,
    current_user_id: int = Depends(get_current_user_id),
    quiz_service: QuizCRUD = Depends(get_quiz_crud),
):
    await quiz_service.delete_quiz(quiz_id=quiz_id, user_id=current_user_id)
    return


@quiz_router.post(
    "/take/",
    response_model=AttemptQuizResult,
    description="Users to take quiz",
    status_code=status.HTTP_200_OK,
)
async def take_quiz(
    attempt_data: AttemptQuizRequest,
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
    current_user: User = Depends(get_current_user),
):
    attempt_results = await quiz_crud.take_quiz(
        user_id=current_user.id, data=attempt_data
    )
    return attempt_results
