from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from poll.db.connection import get_async_session
from poll.db.model_company import CompanyRepository
from poll.db.model_membership import MembershipRepository
from poll.db.model_users import User, UserRepository
from poll.schemas.users import oauth2_scheme
from poll.services.membership_serv import MembershipCRUD
from poll.services.password_hasher import PasswordHasher
from poll.services.users_serv import UserCRUD


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


def get_membership_repository(
    session: AsyncSession = Depends(get_async_session),
) -> MembershipRepository:
    return MembershipRepository(session)


def get_membership_service(
    repo: MembershipRepository = Depends(get_membership_repository),
) -> MembershipCRUD:
    return MembershipCRUD(repo)
