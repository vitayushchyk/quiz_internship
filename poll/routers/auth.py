from datetime import timedelta

from fastapi import APIRouter, Depends, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from poll.core.conf import settings
from poll.core.deps import get_user_crud
from poll.schemas.user_schemas import Auth, Token
from poll.services.auth_serv import create_access_token
from poll.services.exc.user_exc import UserNotAuthenticated
from poll.services.user_serv import UserCRUD

router_auth = APIRouter(prefix="/auth", tags=["auth"])


@router_auth.post("/login/", status_code=status.HTTP_200_OK)
async def login(
    form_data: Auth = Depends(), user_service: UserCRUD = Depends(get_user_crud)
):
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise UserNotAuthenticated
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


async def user_not_authenticated_handler(_: Request, exc: UserNotAuthenticated):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
