class InvitationException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class InvitationAcceptedSuccessfully(InvitationException):
    def __init__(self, status: str):
        super().__init__(
            f"Invitation accepted successfully. Invitation status: {status}."
        )


class PermissionDeniedError(InvitationException):
    def __init__(self):
        super().__init__("Permission denied: you are not the owner of the company.")


class InvitationAlreadyExistError(InvitationException):
    def __init__(self, user_id: int):
        super().__init__(f"Invitation already sent for the user with ID {user_id}.")


class InvitationNotExistsError(InvitationException):
    def __init__(self):
        super().__init__("Invitation not found.")


class InvalidInvitationSearchParams(InvitationException):
    def __init__(self):
        super().__init__(
            "You must provide either invitation_id or company_id and user_id."
        )


class InvitationAlreadyAcceptedError(InvitationException):
    def __init__(self, invitation_id: int):
        super().__init__(
            f"Invitation with ID {invitation_id} has already been accepted."
        )


class InvitationRejectedSuccessfully(InvitationException):
    def __init__(self, status: str):
        super().__init__(f"Invitation with ID {status} has been rejected.")


class InvalidInvitationAlreadyRejectedError(InvitationException):
    def __init__(self, invitation_id: int):
        super().__init__(
            f"Invitation with ID {invitation_id} has already been rejected."
        )


class CannotInviteYourselfError(InvitationException):
    def __init__(self):
        super().__init__(
            "You cannot send an invitation or request to join because you are the owner of this company."
        )


class InvalidActionError(InvitationException):
    def __init__(self, action: str):
        super().__init__(
            f"The action '{action}' is invalid. Please use 'accept' or 'reject'."
        )


class DeniedUserError(InvitationException):
    def __init__(self):
        super().__init__("You do not have permission to perform this action.")
