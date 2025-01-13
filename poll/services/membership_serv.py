from poll.db.model_membership import MembershipRepository, MembershipStatus
from poll.services.exc.membership_exc import UserAlreadyInvited, UserAlreadyMember


class MembershipCRUD:
    def __init__(self, membership_repo: MembershipRepository):
        self.membership_repo = membership_repo

    async def invite_user_to_company(self, company_id: int, user_id: int):
        existing_membership = await self.membership_repo.get_membership(
            company_id, user_id
        )

        if existing_membership:
            if existing_membership.membership_status == MembershipStatus.ACTIVE_MEMBER:
                raise UserAlreadyMember(user_id, company_id)
            elif (
                existing_membership.membership_status
                == MembershipStatus.INVITATION_PENDING
            ):
                raise UserAlreadyInvited(user_id, company_id)

        return await self.membership_repo.add_membership(
            company_id=company_id,
            user_id=user_id,
            status=MembershipStatus.INVITATION_PENDING,
        )

    async def get_user_invitations(self, user_id: int):
        return await self.membership_repo.get_user_invitations(user_id)
