class UserInviteSuccess(Exception):
    def __init__(self, company_id: int, user_id: int):
        self.detail = f"User {user_id} has been successfully invited to the company with ID {company_id}."


class UserAlreadyMember(Exception):
    def __init__(self, company_id: int, user_id: int):
        self.detail = (
            f"User {user_id} is already a member of the company with ID {company_id}."
        )


class UserAlreadyInvited(Exception):
    def __init__(self, company_id: int, user_id: int):
        self.detail = f"User {user_id} is already invited to the company with ID {company_id}, and is waiting for confirmation."
