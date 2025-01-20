class InviteException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class InvitationAcceptedSuccessfully(InviteException):
    def __init__(self, status: str):
        super().__init__(f"Invite accepted successfully invite_status {status}.")


class PermissionDeniedError(InviteException):
    def __init__(self):
        super().__init__(f"Permission denied: you are not the owner of the company.")


class InvitationAlreadyExistError(InviteException):
    def __init__(self, user_id: int):
        super().__init__(f"Invite already send for this user with ID {user_id}")


class InvitationNotExistsError(InviteException):
    def __init__(self):
        super().__init__(f"Invite not found")


class InvalidInviteSearchParams(InviteException):
    def __init__(self):
        super().__init__("You must provide either invite_id or company_id and user_id.")


class InviteAlreadyAcceptedError(InviteException):
    def __init__(self, invite_id: int):
        super().__init__(f"Invite with ID {invite_id} has already been accepted.")


class InviteRejectedSuccessfully(InviteException):
    def __init__(self, status: str):
        super().__init__(f"Invite with ID {status} has been rejected.")


class InvalidInviteAlreadyRejectedError(InviteException):
    def __init__(self, invite_id: int):
        super().__init__(f"Invite with ID {invite_id} has already been rejected.")
