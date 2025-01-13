class MembershipException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class UserInviteSuccess(MembershipException):
    def __init__(self, company_id: int, user_id: int):
        super().__init__(
            f"User {user_id} has been successfully invited to the company with ID {company_id}."
        )


class UserAlreadyMember(MembershipException):
    def __init__(self, company_id: int, user_id: int):
        super().__init__(
            f"User {user_id} is already a member of the company with ID {company_id}."
        )


class UserAlreadyInvited(MembershipException):
    def __init__(self, company_id: int, user_id: int):
        super().__init__(
            f"User {user_id} is already invited to the company with ID {company_id}."
        )
