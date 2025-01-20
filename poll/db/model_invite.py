import datetime
from enum import Enum
from logging import getLogger

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func, select
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from poll.db.connection import Base

logger = getLogger(__name__)


class InviteStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING = "pending"


class Invite(Base):
    __tablename__ = "invites"

    id = Column(Integer, primary_key=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: datetime.datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    invite_status = Column(
        ENUM(InviteStatus, name="invite_status"),
        nullable=False,
    )


class InviteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_invite(self, company_id: int, user_id: int) -> Invite:
        logger.info("Adding invite: %s", company_id)
        new_invite = Invite(
            company_id=company_id, user_id=user_id, invite_status=InviteStatus.PENDING
        )
        self.session.add(new_invite)
        try:
            await self.session.commit()
            await self.session.refresh(new_invite)
        except IntegrityError:
            await self.session.rollback()
            raise
        return new_invite

    async def delete_invite(self, company_id: int, user_id: int) -> None:
        logger.info("Deleting invite: %s", company_id)
        query = select(Invite).where(
            Invite.company_id == company_id, Invite.user_id == user_id
        )
        result = await self.session.execute(query)
        invite = result.scalar()
        if invite:
            await self.session.delete(invite)
            await self.session.commit()

    async def get_invite_by_id(self, company_id: int, user_id: int) -> Invite:
        logger.info("Getting invite: %s", company_id)
        query = select(Invite).where(
            Invite.company_id == company_id, Invite.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar()
