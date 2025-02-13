from typing import List, Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import parse_obj_as
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
    QuizExportResultJSON,
    QuizExportResults,
    QuizRes,
    QuizResult,
    QuizStatusRes,
    ResponseFormat,
    TimePeriodEnum,
    UpdateQuizReq,
    UpdateQuizRes,
    UserRatingRes,
)
from poll.services.quiz_serv import QuizCRUD

# from starlette.responses import StreamingResponse

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
    return AverageScoreRes(average_score=avg_score)


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


@quiz_router.get(
    "/{user_id}/results/",
    description="`Current user` retrieve the quiz-test results ",
    status_code=status.HTTP_200_OK,
)
async def get_user_quiz_results(
    user_id: int,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
):
    return await quiz_crud.get_user_results(
        user_id=user_id, current_user=current_user.id, page=page, page_size=page_size
    )


@quiz_router.get(
    "/{company_id}/results/",
    description="`Owner/Admin` get the quiz results for a company.",
    status_code=status.HTTP_200_OK,
)
async def get_company_quiz_results(
    company_id: int,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
):
    return await quiz_crud.get_company_results(
        company_id=company_id,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )


@quiz_router.get(
    "/company/{company_id}/user/{user_id}/results",
    description="`Owner/Admin` retrieve quiz-test results for a specific user in the specified company",
    status_code=status.HTTP_200_OK,
)
async def get_user_results_in_company(
    company_id: int,
    user_id: int,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
):
    return await quiz_crud.get_user_results_in_company(
        company_id=company_id,
        admin_user_id=current_user.id,
        user_id=user_id,
        page=page,
        page_size=page_size,
    )


@quiz_router.get(
    "/{quiz_id}/export-quiz-result/",
    description="`Owner/Admin` export results of a specific quiz to CSV or JSON format",
    status_code=status.HTTP_200_OK,
)
async def export_quiz_results(
    quiz_id: int,
    response_format: ResponseFormat = ResponseFormat.csv,
    current_user: User = Depends(get_current_user),
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
):
    results = await quiz_crud.get_results_for_quiz(
        quiz_id=quiz_id,
        user_id=current_user.id,
        current_user=current_user.id,
    )

    structured_results = QuizExportResults(
        results=parse_obj_as(List[QuizExportResultJSON], results)
    )

    if response_format == ResponseFormat.json:
        return JSONResponse(content=structured_results.dict())

    elif response_format == ResponseFormat.csv:

        def generate_csv():
            yield "user_id,score,attempts,completed_at\n"
            for result in structured_results.results:
                yield f"{result.user_id},{result.score},{result.attempts},{result.completed_at}\n"

        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=quiz_{quiz_id}_results.csv"
            },
        )


@quiz_router.get(
    "{user_id}/user-rating/",
    description="User rating",
    status_code=status.HTTP_200_OK,
    response_model=UserRatingRes,
)
async def get_user_rating(
    user_id: int,
    page: int = 1,
    page_size: int = 10,
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
    current_user: User = Depends(get_current_user),
):
    user_rating_data = await quiz_crud.get_user_overall_rating(
        user_id=user_id, current_user=current_user.id, page=page, page_size=page_size
    )
    return user_rating_data


@quiz_router.get(
    "/company-average-scores/{company_id}/",
    description="`Owner/Admin` retrieve average quiz scores for all users in company over a specified time period",
    status_code=status.HTTP_200_OK,
)
async def get_average_scores(
    company_id: int,
    time_period: TimePeriodEnum,
    current_user: User = Depends(get_current_user),
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
):
    average_scores = await quiz_crud.get_avg_scores_in_time_period(
        company_id=company_id,
        admin_user_id=current_user.id,
        time_period=time_period,
    )
    return average_scores


@quiz_router.get(
    "/company-user-last-attempts{company_id}/",
    description="`Owner/Admin`  get all users of the company and the time of their last attempt to take the quiz",
    status_code=status.HTTP_200_OK,
)
async def get_company_users_last_attempts(
    company_id: int,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    quiz_crud: QuizCRUD = Depends(get_quiz_crud),
):
    user_attempts = await quiz_crud.get_company_users_last_attempt(
        company_id=company_id, user_id=current_user.id, page=page, page_size=page_size
    )
    return user_attempts
