from typing import List

from fastapi import APIRouter, Depends, status

from poll.core.deps import get_current_user, get_user_crud
from poll.db.model_users import User
from poll.schemas.user_schemas import SignUpReq, UserDetailRes, UserUpdateRes
from poll.services.exc.base_exc import UserForbidden
from poll.services.user_serv import UserCRUD

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get("/", description="Get All Users", response_model=List[UserDetailRes])
async def users_list(page: int = 1, user_service: UserCRUD = Depends(get_user_crud)):
    return await user_service.get_all_users(page=page)


@user_router.get("/me/", response_model=UserDetailRes)
def read_users_me(current_user: int = Depends(get_current_user)):
    return current_user


@user_router.get(
    "/{user_id}/", description="Get User By ID", response_model=UserDetailRes
)
async def user_by_id(user_id: int, user_service: UserCRUD = Depends(get_user_crud)):
    return await user_service.get_user_by_id(user_id)


@user_router.post(
    "/",
    description="Create user",
    status_code=status.HTTP_201_CREATED,
    response_model=UserDetailRes,
)
async def create_user(user: SignUpReq, user_service: UserCRUD = Depends(get_user_crud)):
    return await user_service.create_user(user)


@user_router.put(
    "/{user_id}/",
    description="Update user info",
    status_code=status.HTTP_200_OK,
    response_model=UserUpdateRes,
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


@user_router.delete(
    "/{user_id}/", description="Delete user", status_code=status.HTTP_204_NO_CONTENT
)
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
