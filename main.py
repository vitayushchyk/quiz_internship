import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from poll.core.conf import settings
from poll.routers.auth import router_auth, user_not_authenticated_handler
from poll.routers.company_routers import (
    company_already_exists_handler,
    company_not_found_by_id,
    company_permission_handler,
    company_router,
    company_status_not_valid_handler,
)
from poll.routers.health_check import health_check_router
from poll.routers.invite_routers import (
    company_not_found_by_id_handler,
    invite_accepted_successfully_handler,
    invite_already_accepted_handler,
    invite_already_exists_handler,
    invite_already_rejected_handler,
    invite_not_exists_handler,
    invite_rejected_successfully_handler,
    invite_router,
    permission_denied_handler,
    user_not_found,
)
from poll.routers.users import (
    router_user,
    token_expired_handler,
    token_invalid_handler,
    user_already_exists_handler,
    user_cannot_delete_account_handler,
    user_not_found_handler,
)
from poll.services.exc.auth import JWTTokenExpired, JWTTokenInvalid
from poll.services.exc.company_exc import (
    CompanyAlreadyExist,
    CompanyNotFoundByID,
    CompanyStatusNotValid,
    UnauthorizedCompanyAccess,
)
from poll.services.exc.invite_exc import (
    InvalidInviteAlreadyRejectedError,
    InvitationAcceptedSuccessfully,
    InvitationAlreadyExistError,
    InvitationNotExistsError,
    InviteAlreadyAcceptedError,
    InviteRejectedSuccessfully,
    PermissionDeniedError,
)
from poll.services.exc.user import (
    UserAlreadyExist,
    UserForbidden,
    UserNotAuthenticated,
    UserNotFound,
)

logging.basicConfig()
logging.getLogger().setLevel(settings.get_log_level())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.include_router(health_check_router)
app.include_router(router_user)

app.include_router(router_auth)
app.include_router(company_router)
app.include_router(invite_router)
app.add_exception_handler(UserNotFound, user_not_found_handler)
app.add_exception_handler(UserAlreadyExist, user_already_exists_handler)
app.add_exception_handler(UserNotAuthenticated, user_not_authenticated_handler)
app.add_exception_handler(UserForbidden, user_cannot_delete_account_handler)
app.add_exception_handler(JWTTokenInvalid, token_invalid_handler)
app.add_exception_handler(JWTTokenExpired, token_expired_handler)
app.add_exception_handler(CompanyNotFoundByID, company_not_found_by_id)
app.add_exception_handler(UnauthorizedCompanyAccess, company_permission_handler)
app.add_exception_handler(CompanyAlreadyExist, company_already_exists_handler)
app.add_exception_handler(CompanyStatusNotValid, company_status_not_valid_handler)

# INVITE
app.add_exception_handler(CompanyNotFoundByID, company_not_found_by_id_handler)
app.add_exception_handler(UserNotFound, user_not_found)
app.add_exception_handler(InvitationAlreadyExistError, invite_already_exists_handler)
app.add_exception_handler(PermissionDeniedError, permission_denied_handler)
app.add_exception_handler(InvitationNotExistsError, invite_not_exists_handler)
app.add_exception_handler(InviteAlreadyAcceptedError, invite_already_accepted_handler)
app.add_exception_handler(
    InvalidInviteAlreadyRejectedError, invite_already_rejected_handler
)
app.add_exception_handler(
    InvitationAcceptedSuccessfully, invite_accepted_successfully_handler
)
app.add_exception_handler(
    InviteRejectedSuccessfully, invite_rejected_successfully_handler
)
