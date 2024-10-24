from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from poll.core.conf import settings
from poll.routers.health_check import health_check_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

print('====================================================================================')
print('====================================================================================')
print(settings.db_connection_uri)
print('====================================================================================')
print('====================================================================================')

app.include_router(health_check_router)
