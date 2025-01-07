import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from poll.core.conf import settings
from poll.routers.auth import router_auth, user_not_authenticated_handler
from poll.routers.company_routers import company_not_found_handler, company_router
from poll.routers.health_check import health_check_router
from poll.routers.users import (
    router_user,
    token_expired_handler,
    token_invalid_handler,
    user_already_exists_handler,
    user_cannot_delete_account_handler,
    user_not_found_handler,
)
from poll.services.exc.auth import JWTTokenExpired, JWTTokenInvalid
from poll.services.exc.company_exc import CompanyNotFound
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

app.add_exception_handler(UserNotFound, user_not_found_handler)
app.add_exception_handler(UserAlreadyExist, user_already_exists_handler)
app.add_exception_handler(UserNotAuthenticated, user_not_authenticated_handler)
app.add_exception_handler(UserForbidden, user_cannot_delete_account_handler)
app.add_exception_handler(JWTTokenInvalid, token_invalid_handler)
app.add_exception_handler(JWTTokenExpired, token_expired_handler)
app.add_exception_handler(CompanyNotFound, company_not_found_handler)
