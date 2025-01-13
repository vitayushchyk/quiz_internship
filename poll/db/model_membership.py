import datetime
from enum import Enum
from logging import getLogger

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func, select
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from poll.db.connection import Base

logger = getLogger(__name__)


class MembershipStatus(str, Enum):
    INVITATION_PENDING = "invitation_pending"
    REQUEST_PENDING = "request_pending"
    ACTIVE_MEMBER = "active_member"
    INVITATION_REJECTED = "invitation_rejected"
    REQUEST_REJECTED = "request_rejected"


class Membership(Base):
    __tablename__ = "company_membership"

    id = Column(Integer, primary_key=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: datetime.datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    membership_status = Column(
        ENUM(MembershipStatus, name="membership_status"),
        nullable=False,
    )


class MembershipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_membership(self, company_id: int, user_id: int) -> Membership | None:
        logger.info(
            f"Fetching membership for company_id={company_id}, user_id={user_id}"
        )
        query = select(Membership).filter_by(company_id=company_id, user_id=user_id)
        result = await self.session.execute(query)
        return result.scalar()

    async def add_membership(
        self, company_id: int, user_id: int, status: MembershipStatus
    ) -> Membership:
        logger.info(
            f"Adding membership for company_id={company_id}, user_id={user_id}, status={status}"
        )
        new_membership = Membership(
            company_id=company_id,
            user_id=user_id,
            membership_status=status,
        )
        try:
            self.session.add(new_membership)
            await self.session.commit()
            await self.session.refresh(new_membership)
            logger.info("Membership added successfully.")
            return new_membership
        except IntegrityError:
            logger.error("Integrity error while adding membership.", exc_info=True)
            await self.session.rollback()
            raise

    async def get_user_invitations(self, user_id: int) -> list[Membership]:
        logger.info(f"Fetching invitations for user_id={user_id}")
        query = select(Membership).filter_by(
            user_id=user_id, membership_status=MembershipStatus.INVITATION_PENDING
        )
        result = await self.session.execute(query)
        return result.scalars().all()
