from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette import status

from poll.core.deps import get_current_user_id, get_membership_service
from poll.schemas.membership_schemas import InvitationStatusDetailRes, InviteSuccessRes
from poll.services.exc.membership_exc import (
    UserAlreadyInvited,
    UserAlreadyMember,
    UserInviteSuccess,
)
from poll.services.membership_serv import MembershipCRUD

membership_router = APIRouter(prefix="/membership", tags=["Membership"])


@membership_router.post(
    "/{company_id}/invite/",
    response_model=InviteSuccessRes,
    summary="Invite a user to a company",
    description="Invites a user to join the specified company if the user is not already invited or a member.",
)
async def invite_user_to_company(
    company_id: int,
    user_id: int,
    membership_service: MembershipCRUD = Depends(get_membership_service),
):
    try:
        new_membership = await membership_service.invite_user_to_company(
            company_id, user_id
        )
        return InviteSuccessRes(
            company_id=company_id,
            user_id=user_id,
            membership_status=new_membership.membership_status.value,
        )
    except UserAlreadyMember:
        raise UserAlreadyMember(user_id=user_id, company_id=company_id)
    except UserAlreadyInvited:
        raise UserAlreadyInvited(user_id=user_id, company_id=company_id)


from typing import List


@membership_router.get(
    "/my_invitations",
    response_model=List[InvitationStatusDetailRes],
    summary="View active invitations",
    description="Retrieve all active invitations for the currently authenticated user.",
)
async def view_active_invitations(
    user_id: int = Depends(get_current_user_id),
    membership_service: MembershipCRUD = Depends(get_membership_service),
):
    invitations = await membership_service.get_user_invitations(user_id)

    return [
        InvitationStatusDetailRes(
            company_id=inv.company_id,
            user_id=inv.user_id,
            membership_status=inv.membership_status.value,
        )
        for inv in invitations
    ]


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
