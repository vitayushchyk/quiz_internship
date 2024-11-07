import datetime
from logging import getLogger
from typing import Any, Sequence

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    Row,
    RowMapping,
    String,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from poll.db.connection import Base
from poll.schemas.users import SignUpReq, UserUpdateRes
from poll.services.exc.user import UserNotFound
from poll.services.pagination import Pagination
from poll.services.password_hasher import PasswordHasher

logger = getLogger(__name__)


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, nullable=False)
    first_name: str = Column(String)
    last_name: str = Column(String)
    email: str = Column(String, unique=True, nullable=False)
    password: str = Column(String, nullable=False)
    is_active: bool = Column(Boolean, default=False, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    created_at: datetime.date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class UserRepository:
    def __init__(self, session: AsyncSession, hasher: PasswordHasher = None):
        self.session = session
        self.hasher = hasher

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
        result = (await self.session.execute(query)).scalar()
        if result is None:
            raise UserNotFound(user_id)
        return result

    async def create_user(self, user: SignUpReq) -> User:
        logger.info("Creating user: %s", user)
        model_dump = user.model_dump()
        model_dump["password"] = self.hasher.hash_password(user.password)
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
            raise UserNotFound(user_id)
        for field, value in user_upd.dict(exclude_unset=True).items():
            setattr(user, field, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> User:
        logger.info("Deleting user: %s", user_id)
        result = await self.session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise UserNotFound(user_id)
        await self.session.delete(user)
        await self.session.commit()
        return user
