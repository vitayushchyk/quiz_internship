class InviteException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class UserAlreadyInvited(InviteException):
    def __init__(self, company_id: int, user_id: int):
        super().__init__(
            f"User {user_id} is already invited to the company with ID {company_id}."
        )


class PermissionDeniedError(InviteException):
    def __init__(self):
        super().__init__(f"Permission denied: you are not the owner of the company.")


class InvitationAlreadyExistError(InviteException):
    def __init__(self, user_id: int):
        super().__init__(f"Invite already send for this user with ID {user_id}")


class InvitationNotExistsError(InviteException):
    def __init__(
        self,
    ):
        super().__init__(f"Invite not found")
