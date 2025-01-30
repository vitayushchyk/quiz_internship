from fastapi import HTTPException


class MeduzzenBaseHttpException(HTTPException): ...


class UserAlreadyExist(MeduzzenBaseHttpException):
    def __init__(self, user_email: str):
        super().__init__(
            status_code=409, detail=f"User with email '{user_email}' already exists."
        )


class UserNotAuthenticated(MeduzzenBaseHttpException):
    def __init__(self):
        super().__init__(status_code=401, detail=f"Not authenticated")


class UserForbidden(MeduzzenBaseHttpException):
    def __init__(self):
        super().__init__(
            status_code=403, detail="Access to the requested resource is forbidden."
        )


class UserNotMemberError(MeduzzenBaseHttpException):
    def __init__(self):
        super().__init__(status_code=404, detail="User is not a member of the company.")


class UserAlreadyMemberError(MeduzzenBaseHttpException):
    def __init__(self, company_id: int, role: str, user_id: int):
        super().__init__(
            status_code=409,
            detail=f"User with ID {user_id} is already a member of the company with ID {company_id} "
            f"and has role {role.upper()}.",
        )


class UserNotFound(MeduzzenBaseHttpException):
    def __init__(self, user_id: int):
        super().__init__(status_code=404, detail=f"User with ID {user_id} not found.")


class JWTTokenInvalid(MeduzzenBaseHttpException):
    def __init__(self):
        super().__init__(status_code=401, detail=f"JWT Token invalid.")


class CompanyNotFoundByID(MeduzzenBaseHttpException):
    def __init__(self, company_id: int):
        super().__init__(
            status_code=404, detail=f"Company with ID {company_id} not found."
        )


class UnauthorizedCompanyAccess(MeduzzenBaseHttpException):
    def __init__(self, company_id: int):
        super().__init__(
            status_code=403,
            detail=f"Unauthorized access to company with ID {company_id}.",
        )


class CompanyAlreadyExist(MeduzzenBaseHttpException):
    def __init__(self, company_name: str):
        super().__init__(
            status_code=409, detail=f"Company with name {company_name} already exists."
        )


class CompanyStatusNotValid(MeduzzenBaseHttpException):
    def __init__(self, company_status: str, valid_statuses: list):
        super().__init__(
            status_code=400,
            detail=f"Invalid company status: {company_status}."
            f"Available statuses are: {', '.join(valid_statuses)}.",
        )


class PermissionDeniedError(MeduzzenBaseHttpException):
    def __init__(self, required_roles: list[str]):
        roles_list = ", ".join(required_roles)
        super().__init__(
            status_code=403,
            detail=f"Role [{roles_list}] are required for this operation.",
        )


class PermissionUserError(MeduzzenBaseHttpException):
    def __init__(self, invite_id: int):
        super().__init__(
            status_code=403,
            detail=f"Permission denied: you do not have permission to modify the invitation with ID {invite_id}.",
        )


class InvitationAlreadyExist(MeduzzenBaseHttpException):
    def __init__(self):
        super().__init__(
            status_code=409, detail=f"Invitation already has been sent successfully."
        )


class InvitationNotExistsError(MeduzzenBaseHttpException):
    def __init__(self):
        super().__init__(status_code=404, detail=f"Invitation not found")


class InvalidActionError(MeduzzenBaseHttpException):
    def __init__(self, status: str):
        super().__init__(
            status_code=400,
            detail=f"Unsupported {status}. Please use 'accepted' or 'rejected'.",
        )


class InvitationActionSuccess(MeduzzenBaseHttpException):
    def __init__(self, status: str, company_id: int):
        super().__init__(
            status_code=200,
            detail=f"Successfully {status.upper()} the invitation for the company with ID: {company_id}.",
        )


class CannotInviteYourselfError(MeduzzenBaseHttpException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="You cannot send an invitation or request to join because you are the owner of this company.",
        )


class CannotDeleteYourselfError(MeduzzenBaseHttpException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="You cannot remove yourself from the company."
        )


class InvalidInvitationSearchParams(MeduzzenBaseHttpException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="You must provide either invitation_id or company_id and user_id.",
        )


class InvalidEmailError(MeduzzenBaseHttpException):
    def __init__(self, email: str):
        super().__init__(
            status_code=400,
            detail=f"Invalid email format provided: {email}. Please provide a valid email address.",
        )
