from poll.db.model_membership import MembershipRepository


class MembershipCRUD:
    def __init__(self, membership_repo: MembershipRepository):
        self.membership_repo = membership_repo

    async def invite_user_to_company(self, company_id, user_id):
        return await self.membership_repo.invite_user_to_company(company_id, user_id)
