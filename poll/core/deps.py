from typing import Annotated, Any, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from poll.db.connection import RedisDependency, get_async_session
from poll.db.model_company import CompanyRepository
from poll.db.model_invite import InviteRepository
from poll.db.model_notification import NotificationRepository
from poll.db.model_quiz import QuizRepository
from poll.db.model_users import User, UserRepository
from poll.schemas.user_schemas import oauth2_scheme
from poll.services.invite_serv import InviteCRUD
from poll.services.notification_ser import NotificationCRUD
from poll.services.password_hasher import PasswordHasher
from poll.services.quiz_serv import QuizCRUD
from poll.services.scheduler_ser import SchedulerService
from poll.services.user_serv import UserCRUD


async def get_password_hasher():
    yield PasswordHasher()


async def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[UserRepository, None]:
    yield UserRepository(session)


async def get_user_crud(
    user_repository: UserRepository = Depends(get_user_repository),
    hasher: PasswordHasher = Depends(get_password_hasher),
) -> AsyncGenerator[UserCRUD, None]:
    yield UserCRUD(user_repository, hasher)


async def get_current_user(
    jwt_token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserCRUD = Depends(get_user_crud),
) -> AsyncGenerator[User | None, None]:
    yield await user_service.get_current_user(jwt_token)


async def get_current_user_id(
    current_user: User = Depends(get_current_user),
) -> int:
    return current_user.id


async def get_company_repository(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[CompanyRepository, None]:
    yield CompanyRepository(session)


async def get_invite_repository(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[InviteRepository, None]:
    yield InviteRepository(session)


async def get_invite_crud(
    invite_repository: InviteRepository = Depends(get_invite_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    company_repository: CompanyRepository = Depends(get_company_repository),
) -> AsyncGenerator[InviteCRUD, None]:
    yield InviteCRUD(invite_repository, user_repository, company_repository)


async def get_quiz_repository(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[QuizRepository, None]:
    yield QuizRepository(session)


async def get_redis_client() -> AsyncGenerator[Any, Any]:
    yield RedisDependency()


async def get_quiz_crud(
    quiz_repository: QuizRepository = Depends(get_quiz_repository),
    company_repository: CompanyRepository = Depends(get_company_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> AsyncGenerator[QuizCRUD, None]:
    yield QuizCRUD(quiz_repository, company_repository, user_repository)


async def get_notification_repository(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[NotificationRepository, None]:
    yield NotificationRepository(session)


async def get_notification_crud(
    notification_repository: NotificationRepository = Depends(
        get_notification_repository
    ),
) -> AsyncGenerator[NotificationCRUD, None]:
    yield NotificationCRUD(notification_repository)


async def get_scheduler() -> SchedulerService:
    async_session_generator = get_async_session()

    try:

        session = await anext(async_session_generator)
        quiz_repository = QuizRepository(session)
        notification_repository = NotificationRepository(session)
        user_repository = UserRepository(session)
        company_repository = CompanyRepository(session)
        quiz_service = QuizCRUD(quiz_repository, company_repository, user_repository)
        notification_service = NotificationCRUD(notification_repository)

        return SchedulerService(
            quiz_service=quiz_service, notification_service=notification_service
        )

    finally:
        await async_session_generator.aclose()
