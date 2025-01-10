import datetime
from enum import Enum
from logging import getLogger

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func, select
from sqlalchemy.dialects.postgresql import ENUM

from poll.db.connection import Base
from poll.services.exc.membership_exc import UserAlreadyInvited, UserAlreadyMember

logger = getLogger(__name__)


class MembershipStatus(str, Enum):
    PENDING_INVITATION = "pending_invitation"
    PENDING_REQUEST = "pending_request"
    MEMBER = "member"


class CompanyMembership(Base):
    __tablename__ = "company_membership"

    id = Column(Integer, primary_key=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: datetime.date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    membership_status = Column(
        ENUM(MembershipStatus, name="membership_status"),
        nullable=False,
    )


class MembershipRepository:
    def __init__(
        self,
        session,
    ):
        self.session = session

    async def invite_user_to_company(self, company_id: int, user_id: int):
        query = select(CompanyMembership).filter_by(
            company_id=company_id, user_id=user_id
        )
        existing_membership = (await self.session.execute(query)).scalar()

        if existing_membership:
            if existing_membership.membership_status == MembershipStatus.MEMBER:
                raise UserAlreadyMember(user_id, company_id)
            elif (
                existing_membership.membership_status
                == MembershipStatus.PENDING_INVITATION
            ):
                raise UserAlreadyInvited(user_id, company_id)

        new_membership = CompanyMembership(
            company_id=company_id,
            user_id=user_id,
            membership_status=MembershipStatus.PENDING_INVITATION,
        )
        self.session.add(new_membership)
        await self.session.commit()
        await self.session.refresh(new_membership)
        return new_membership

    async def get_user_invitations(self, user_id: int):
        query = select(CompanyMembership).filter_by(
            user_id=user_id, membership_status=MembershipStatus.PENDING_INVITATION
        )
        result = (await self.session.execute(query)).scalars().all()
        return result
