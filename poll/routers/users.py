from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from poll.core.deps import get_user_crud
from poll.schemas.users import SignUpReq, UserDetailRes, UserUpdateRes
from poll.services.exc.user import UserAlreadyExist, UserNotFound
from poll.services.users import UserCRUD

router_user = APIRouter(prefix="/user")


@router_user.get("/list/", summary="Get All Users", response_model=List[UserDetailRes])
async def users_list(page: int = 1, user_service: UserCRUD = Depends(get_user_crud)):
    return await user_service.get_all_users(page=page)


@router_user.get("/{user_id}/", summary="Get User By ID", response_model=UserDetailRes)
async def user_by_id(user_id: int, user_service: UserCRUD = Depends(get_user_crud)):
    return await user_service.get_user_by_id(user_id)


@router_user.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=UserDetailRes
)
async def create_user(user: SignUpReq, user_service: UserCRUD = Depends(get_user_crud)):
    return await user_service.create_user(user)


@router_user.put(
    "/{user_id}/", status_code=status.HTTP_200_OK, response_model=UserUpdateRes
)
async def update_user(
    user_id: int,
    user_update: UserUpdateRes,
    user_service: UserCRUD = Depends(get_user_crud),
):
    return await user_service.update_user(user_id, user_update)


@router_user.delete("/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, user_service: UserCRUD = Depends(get_user_crud)):
    await user_service.delete_user(user_id)


async def user_not_found_handler(_: Request, exc: UserNotFound):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def user_already_exists_handler(_: Request, exc: UserAlreadyExist):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_409_CONFLICT,
    )
