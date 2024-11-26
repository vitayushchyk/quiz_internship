from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from poll.db.connection import get_async_session
from poll.db.model_users import User, UserRepository
from poll.services.password_hasher import PasswordHasher
from poll.services.users_serv import UserCRUD, oauth2_scheme


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
