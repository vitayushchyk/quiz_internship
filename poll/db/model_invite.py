import datetime
from enum import Enum
from logging import getLogger

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func, select
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from poll.db.connection import Base
from poll.services.exc.invite_exc import (
    InvalidInviteSearchParams,
    InvitationNotExistsError,
)

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

    async def get_invite_by_id(
        self, invite_id: int = None, company_id: int = None, user_id: int = None
    ) -> Invite:
        if invite_id:
            logger.info("Getting invite by ID: %s", invite_id)
            query = select(Invite).where(Invite.id == invite_id)
        elif company_id and user_id:
            logger.info(
                "Getting invite by Company ID: %s and User ID: %s", company_id, user_id
            )
            query = select(Invite).where(
                Invite.company_id == company_id, Invite.user_id == user_id
            )
        else:
            raise InvalidInviteSearchParams

        result = await self.session.execute(query)
        return result.scalar()

    async def get_user_invites(self, user_id: int) -> list[Invite]:
        logger.info("Getting invites for user_id: %s", user_id)
        query = select(Invite).where(Invite.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def accept_invite(self, invite_id: int) -> Invite:
        logger.info("User accepting invite with id: %s", invite_id)
        query = select(Invite).where(Invite.id == invite_id)
        result = await self.session.execute(query)
        invite = result.scalar()

        if not invite:
            raise InvitationNotExistsError

        invite.invite_status = InviteStatus.ACCEPTED
        await self.session.commit()
        await self.session.refresh(invite)
        return invite

    async def reject_invite(self, invite_id: int):
        logger.info("User rejecting invite with id: %s", invite_id)

        query = select(Invite).where(Invite.id == invite_id)
        result = await self.session.execute(query)
        invite = result.scalar()

        if not invite:
            raise InvitationNotExistsError

        invite.invite_status = InviteStatus.REJECTED
        await self.session.commit()
        return invite
