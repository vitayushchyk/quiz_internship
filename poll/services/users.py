from logging import getLogger
from typing import Any, AsyncGenerator, Sequence

from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy import Row, RowMapping, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from poll.db.connection import get_async_session
from poll.db.model_users import User
from poll.schemas.users import SignUpReq, UserUpdateRes
from poll.services.pagination import Pagination

logger = getLogger(__name__)


class UserCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users(
        self, page: int = 1, page_size: int = 10
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        logger.info("Fetching all users (page: %s, page_size: %s)", page, page_size)
        paginator = Pagination(self.session, select(User), page, page_size)
        paginate_users = await paginator.fetch_results()
        return paginate_users

    async def get_user_by_id(self, user_id: int) -> User | None:
        logger.info("Fetching user by ID: %s", user_id)
        query = select(User).filter(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar()

    async def create_user(self, user: SignUpReq) -> User:
        logger.info("Creating user: %s", user)
        model_dump = user.model_dump()
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        model_dump["password"] = pwd_context.hash(model_dump["password"])
        new_user = User(**model_dump)
        self.session.add(new_user)

        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def update_user(self, user_id: int, user_upd: UserUpdateRes) -> User:
        logger.info("Updating user: %s", user_upd)
        result = await self.session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if user is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
        for field, value in user_upd.dict(exclude_unset=True).items():
            setattr(user, field, value)
        await self.session.commit()
        return user

    async def delete_user(self, user_id: int) -> User:
        logger.info("Deleting user: %s", user_id)
        result = await self.session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        await self.session.delete(user)
        await self.session.commit()
        return user


async def get_user_crud(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[UserCRUD, None]:
    yield UserCRUD(session)
