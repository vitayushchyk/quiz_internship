from typing import List, Optional

from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis

from poll.core.deps import get_current_user, get_current_user_id, get_quiz_crud
from poll.db.connection import get_redis_client
from poll.db.model_quiz import QuizStatus
from poll.db.model_users import User
from poll.schemas.quiz_shemas import (
    AttemptQuizRequest,
    AverageScoreRes,
    CreateQuizReq,
    PublicOptionData,
    PublicQuestionData,
    PublicQuizRes,
    QuizRes,
    QuizResult,
    QuizStatusRes,
    UpdateQuizReq,
    UpdateQuizRes,
)
from poll.services.quiz_serv import QuizCRUD

quiz_router = APIRouter(prefix="/quiz", tags=["Quiz"])


@quiz_router.post(
    "/create_quiz/",
    response_model=QuizRes,
    description="`Owner/Admin` create quiz",
    status_code=status.HTTP_201_CREATED,
)
async def create_quiz(
    company_id: int,
    data: CreateQuizReq,
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
    "/{quiz_id}/quiz-title/",
    response_model=UpdateQuizRes,
    description="`Owner/Admin` update quiz title",
    status_code=status.HTTP_200_OK,
)
async def update_quiz(
    quiz_id: int,
    title_req: UpdateQuizReq,
    current_user_id: int = Depends(get_current_user_id),
    quiz_service: "QuizCRUD" = Depends(get_quiz_crud),
):
    new_title = title_req.new_title
    updated_quiz = await quiz_service.editing_quiz_title(
        quiz_id=quiz_id, user_id=current_user_id, title=new_title
    )

    return UpdateQuizRes(id=updated_quiz.id, new_title=updated_quiz.title)


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


@quiz_router.get(
    "/by-status/",
    response_model=List[QuizStatusRes],
    description="Get all quiz's by status ",
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
    response_model=QuizResult,
    description="Users to take quiz",
    status_code=status.HTTP_200_OK,
)
async def take_quiz(
    attempt_data: AttemptQuizRequest,
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
    redis: Redis = Depends(get_redis_client),
    current_user: User = Depends(get_current_user),
):
    attempt_results = await quiz_crud.take_quiz(
        user_id=current_user.id, data=attempt_data, redis=redis
    )
    return attempt_results


@quiz_router.get(
    "/average-score/",
    description="Get average quiz score for user or system-wide",
    status_code=status.HTTP_200_OK,
    response_model=AverageScoreRes,
)
async def get_average_score(
    user_id: int = Depends(get_current_user_id),
    company_id: Optional[int] = None,
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
):
    if company_id:
        avg_score = await quiz_crud.quiz_repo.get_avg_score(
            user_id=user_id, company_id=company_id
        )
    else:
        avg_score = await quiz_crud.quiz_repo.get_system_avg_score()
    return AverageScoreRes(avg_score=avg_score)


@quiz_router.get(
    "/{quiz_id}",
    description="Get all quiz's by id",
    status_code=status.HTTP_200_OK,
    response_model=PublicQuizRes,
)
async def get_quiz_by_id(
    quiz_id: int,
    quiz_service: QuizCRUD = Depends(get_quiz_crud),
):
    quiz = await quiz_service.get_quiz_by_id(quiz_id=quiz_id)

    questions = []
    for question in quiz.questions:
        question_data = PublicQuestionData(
            title=question.title,
            options=[
                PublicOptionData(text=option.option_text) for option in question.options
            ],
        )
        questions.append(question_data)

    return PublicQuizRes(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        questions=questions,
        company_id=quiz.company_id,
        creator_id=quiz.created_by,
    )
