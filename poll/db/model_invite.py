import datetime
from enum import Enum
from logging import getLogger

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func, select
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from poll.db.connection import Base
from poll.services.exc.base_exc import (
    InvalidInvitationSearchParams,
    InvitationAlreadyExist,
    InvitationNotExistsError,
)

logger = getLogger(__name__)


class InviteStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING = "pending"


class Invite(Base):
    __tablename__ = "invites"

    id: int = Column(Integer, primary_key=True, nullable=False)
    company_id: int = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)

    invite_status: InviteStatus = Column(
        ENUM(InviteStatus, name="invite_status"),
        nullable=False,
    )
    created_at: datetime.datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime.datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class InviteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_invite(self, company_id: int, user_id: int) -> Invite:
        logger.info(f"Adding invite: (company_id={company_id}, user_id={user_id})")
        new_invite = Invite(
            company_id=company_id, user_id=user_id, invite_status=InviteStatus.PENDING
        )
        self.session.add(new_invite)
        try:
            await self.session.commit()
            await self.session.refresh(new_invite)
        except IntegrityError:
            await self.session.rollback()
            raise InvitationAlreadyExist()
        return new_invite

    async def delete_invite(self, company_id: int, user_id: int) -> bool:
        logger.info(f"Deleting invite: (company_id={company_id}, user_id={user_id})")

        query = select(Invite).where(
            Invite.company_id == company_id, Invite.user_id == user_id
        )
        result = await self.session.execute(query)
        invite = result.scalar()

        if invite:
            await self.session.delete(invite)
            await self.session.commit()
            return True

        return False

    async def get_invite(
        self,
        invite_id: int = None,
        company_id: int = None,
        user_id: int = None,
        invite_status: InviteStatus = None,
        only_one: bool = False,
    ) -> list[Invite] | Invite:
        logger.info(
            f"Fetching invites ({invite_id=}, {company_id=}, {user_id=}, {invite_status=})"
        )
        filters = []
        if invite_id:
            filters.append(Invite.id == invite_id)
        if company_id:
            filters.append(Invite.company_id == company_id)
        if user_id:
            filters.append(Invite.user_id == user_id)
        if invite_status:
            filters.append(Invite.invite_status == invite_status)

        if not filters:
            raise InvalidInvitationSearchParams()
        query = select(Invite).where(*filters)
        result = await self.session.execute(query)

        if only_one:
            return result.scalar()
        return result.scalars().all()

    async def update_invite_status(
        self, invite_id: int, new_status: InviteStatus
    ) -> Invite:
        logger.info(
            f"Updating invite status: (invite_id={invite_id}, new_status={new_status})"
        )
        query = select(Invite).where(Invite.id == invite_id)
        result = await self.session.execute(query)
        invite = result.scalar()

        if not invite:
            raise InvitationNotExistsError
        invite.invite_status = new_status

        await self.session.commit()
        await self.session.refresh(invite)
        return invite
