import datetime
from enum import Enum
from logging import getLogger

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func, select
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from poll.db.connection import Base
from poll.services.exc.invite_exc import (
    InvalidInvitationSearchParams,
    InvitationAlreadyExistError,
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
            raise InvitationAlreadyExistError(user_id)
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
        self, invite_id: int = None, company_id: int = None, user_id: int = None
    ) -> Invite:
        logger.info(f"Fetching invite ({invite_id=}, {company_id=}, {user_id=})")
        query = None
        if invite_id:
            query = select(Invite).where(Invite.id == invite_id)
        elif company_id and user_id:
            query = select(Invite).where(
                Invite.company_id == company_id, Invite.user_id == user_id
            )
        else:
            raise InvalidInvitationSearchParams

        result = await self.session.execute(query)
        return result.scalar()

    async def get_user_invites(self, user_id: int) -> list[Invite]:
        logger.info(f"Fetching invites for user_id: {user_id}")
        query = select(Invite).where(Invite.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_invite_status(
        self, invite_id: int, new_status: InviteStatus
    ) -> Invite:
        logger.info(
            f"Updating invite status: (invite_id={invite_id}, status={new_status})"
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
