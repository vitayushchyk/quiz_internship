from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
)

from poll.schemas.users import SignUpReq, UserDetailRes, UserUpdateRes
from poll.services.users import get_user_crud

router_user = APIRouter(prefix="/user")


@router_user.get("/list/", summary="Get All Users", response_model=List[UserDetailRes])
async def users_list(page: int = 1, user_service=Depends(get_user_crud)):
    users = await user_service.get_all_users(page=page)
    return users


@router_user.get("/{user_id}/", summary="Get User By ID", response_model=UserDetailRes)
async def user_by_id(user_id: int, user_service=Depends(get_user_crud)):
    if (user := await user_service.get_user_by_id(user_id)) is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found"
        )
    return user


@router_user.post("/", status_code=HTTP_201_CREATED, response_model=UserDetailRes)
async def create_user(
    user: SignUpReq,
    user_service=Depends(get_user_crud),
):
    new_user = await user_service.create_user(user)
    return new_user


@router_user.put("/{user_id}/", status_code=HTTP_200_OK, response_model=UserUpdateRes)
async def update_user(
    user_id: int,
    user_update: UserUpdateRes,
    user_service=Depends(get_user_crud),
):
    await user_service.update_user(user_id, user_update)
    return user_update


@router_user.delete("/{user_id}/", status_code=HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, user_service=Depends(get_user_crud)):
    await user_service.delete_user(user_id)
