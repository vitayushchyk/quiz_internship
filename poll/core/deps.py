from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from poll.db.connection import get_async_session
from poll.db.model_users import UserRepository
from poll.services.password_hasher import PasswordHasher
from poll.services.users import UserCRUD


async def get_password_hasher():
    yield PasswordHasher()


async def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
    hasher: PasswordHasher = Depends(get_password_hasher),
) -> AsyncGenerator[UserRepository, None]:
    yield UserRepository(session, hasher)


async def get_user_crud(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AsyncGenerator[UserCRUD, None]:
    yield UserCRUD(user_repository)
