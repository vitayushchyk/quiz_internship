from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette import status

from poll.core.deps import get_membership_repository
from poll.services.exc.membership_exc import (
    UserAlreadyInvited,
    UserAlreadyMember,
    UserInviteSuccess,
)
from poll.services.membership_serv import MembershipCRUD

membership_router = APIRouter(prefix="/membership", tags=["membership"])


@membership_router.post("/{company_id}/invite/", summary="Invite a user to the company")
async def invite_user_to_company(
    company_id: int,
    user_id: int,
    membership_service: MembershipCRUD = Depends(get_membership_repository),
):
    try:
        await membership_service.invite_user_to_company(company_id, user_id)
        return UserInviteSuccess(company_id=company_id, user_id=user_id)
    except UserAlreadyMember:
        raise UserAlreadyMember(user_id=user_id, company_id=company_id)


async def user_invite_to_company_handler(_: Request, exc: UserInviteSuccess):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_200_OK,
    )


async def user_already_member_handler(_: Request, exc: UserAlreadyMember):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_409_CONFLICT,
    )


async def user_already_invite_handler(_: Request, exc: UserAlreadyInvited):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_409_CONFLICT,
    )
