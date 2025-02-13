import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from poll.core.conf import settings
from poll.routers.auth_routers import router_auth
from poll.routers.company_routers import company_router
from poll.routers.health_check_routers import health_check_router
from poll.routers.invite_routers import invite_router
from poll.routers.notification_routers import notification_router
from poll.routers.quiz_routers import quiz_router
from poll.routers.user_routers import user_router

logging.basicConfig()
logging.getLogger().setLevel(settings.get_log_level())

app = FastAPI(
    title="Quiz app",
    docs_url="/docs",
    description="Application for internship at meduzzen",
    debug=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.include_router(health_check_router)
app.include_router(user_router)

app.include_router(router_auth)
app.include_router(company_router)
app.include_router(invite_router)

app.include_router(quiz_router)
app.include_router(notification_router)
