import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from poll.core.conf import settings
from poll.routers.health_check import health_check_router
from poll.routers.users import (
    router_user,
    user_already_exists_handler,
    user_not_found_handler,
)
from poll.services.exc.user import UserAlreadyExist, UserNotFound

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

app.add_exception_handler(UserNotFound, user_not_found_handler)
app.add_exception_handler(UserAlreadyExist, user_already_exists_handler)
