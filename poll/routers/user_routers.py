from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from poll.core.deps import (
    get_current_user,
    get_current_user_id,
    get_invite_crud,
    get_user_crud,
)
from poll.db.model_users import User
from poll.schemas.user_schemas import SignUpReq, UserDetailRes, UserUpdateRes
from poll.services.exc.auth_exc import JWTTokenExpired, JWTTokenInvalid
from poll.services.exc.user_exc import (
    UserAlreadyExist,
    UserForbidden,
    UserNotFound,
    UserNotMemberError,
)
from poll.services.invite_serv import InviteCRUD
from poll.services.user_serv import UserCRUD

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/list/", summary="Get All Users", response_model=List[UserDetailRes])
async def users_list(page: int = 1, user_service: UserCRUD = Depends(get_user_crud)):
    return await user_service.get_all_users(page=page)


@user_router.get("/me/", response_model=UserDetailRes)
def read_users_me(current_user: int = Depends(get_current_user)):
    return current_user


@user_router.get("/{user_id}/", summary="Get User By ID", response_model=UserDetailRes)
async def user_by_id(user_id: int, user_service: UserCRUD = Depends(get_user_crud)):
    return await user_service.get_user_by_id(user_id)


@user_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=UserDetailRes
)
async def create_user(user: SignUpReq, user_service: UserCRUD = Depends(get_user_crud)):
    return await user_service.create_user(user)


@user_router.put(
    "/{user_id}/", status_code=status.HTTP_200_OK, response_model=UserUpdateRes
)
async def update_user(
    user_id: int,
    user_update: UserUpdateRes,
    current_user: User = Depends(get_current_user),
    user_service: UserCRUD = Depends(get_user_crud),
):
    return await user_service.update_user(
        user_id=user_id, user_update=user_update, current_user=current_user
    )


@user_router.delete("/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user_crud: UserCRUD = Depends(get_user_crud),
):
    try:
        await user_crud.delete_user(user_id=user_id, current_user=current_user)
    except UserForbidden:
        raise UserForbidden
    return


@user_router.delete(
    "/leave/{company_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User leaves the company",
)
async def leave_company(
    company_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    await invite_service.user_leave_company(
        company_id=company_id, current_user_id=current_user_id
    )


async def user_not_found_handler(_: Request, exc: UserNotFound):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def user_cannot_delete_account_handler(_: Request, exc: UserForbidden):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_403_FORBIDDEN,
    )


async def user_already_exists_handler(_: Request, exc: UserAlreadyExist):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_409_CONFLICT,
    )


async def user_not_member_of_company_handler(_: Request, exc: UserNotMemberError):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def token_invalid_handler(_: Request, exc: JWTTokenInvalid):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


async def token_expired_handler(_: Request, exc: JWTTokenExpired):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
