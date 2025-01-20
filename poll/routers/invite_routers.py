from typing import List

from fastapi import APIRouter, Depends
from requests import Request
from starlette import status
from starlette.responses import JSONResponse

from poll.core.deps import get_current_user_id, get_invite_crud
from poll.schemas.invite_schemas import InviteCreateReq, InviteRes
from poll.services.exc.company_exc import CompanyNotFoundByID
from poll.services.exc.invite_exc import (
    InvalidInviteAlreadyRejectedError,
    InvitationAcceptedSuccessfully,
    InvitationAlreadyExistError,
    InvitationNotExistsError,
    InviteRejectedSuccessfully,
    PermissionDeniedError,
)
from poll.services.exc.user import UserNotFound
from poll.services.invite_serv import InviteCRUD

invite_router = APIRouter(prefix="/invite", tags=["Invite"])


@invite_router.post(
    "/",
    response_model=InviteRes,
    status_code=status.HTTP_201_CREATED,
    summary="Create Invite",
)
async def create_invite_to_user(
    request: InviteCreateReq,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    try:

        invite = await invite_service.owner_send_invite(
            company_id=request.company_id,
            user_id=request.user_id,
            current_user_id=current_user_id,
        )

        response = InviteRes(
            id=invite.id,
            company_id=invite.company_id,
            user_id=invite.user_id,
            invite_status=invite.invite_status.value,
        )
        return response
    except PermissionDeniedError:
        raise PermissionDeniedError


@invite_router.delete(
    "/{company_id}/{user_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel Invite",
)
async def cancel_invite_to_user(
    company_id: int,
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    result = await invite_service.owner_cancel_invite(
        company_id=company_id,
        user_id=user_id,
        current_user_id=current_user_id,
    )
    return result


@invite_router.put(
    "/{invite_id}/accept/", status_code=status.HTTP_200_OK, summary="Accept Invite"
)
async def accept_invite(
    invite_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    invite = await invite_service.user_accept_invite(
        invite_id=invite_id,
        current_user_id=current_user_id,
    )
    return InvitationAcceptedSuccessfully(status=invite.invite_status.value)


@invite_router.put(
    "/{invite_id}/reject/", status_code=status.HTTP_200_OK, summary="Reject Invite"
)
async def reject_invite(
    invite_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    rej_invite = await invite_service.user_reject_invite(
        invite_id=invite_id,
        current_user_id=current_user_id,
    )
    return InviteRejectedSuccessfully(status=rej_invite.invite_status.value)


@invite_router.get(
    "/my-invites",
    response_model=List[InviteRes],
    summary="Get all invites for the authenticated user",
)
async def get_user_invites(
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    invites = await invite_service.show_user_invites(current_user_id=current_user_id)
    return invites


async def company_not_found_by_id_handler(_: Request, exc: CompanyNotFoundByID):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def user_not_found(_: Request, exc: UserNotFound):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def invite_already_exists_handler(_: Request, exc: InvitationAlreadyExistError):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_409_CONFLICT,
    )


async def permission_denied_handler(_: Request, exc: PermissionDeniedError):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_403_FORBIDDEN,
    )


async def invite_not_exists_handler(_: Request, exc: InvitationNotExistsError):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def invite_already_accepted_handler(_: Request, exc: InvitationAlreadyExistError):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_409_CONFLICT,
    )


async def invite_accepted_successfully_handler(
    _: Request, exc: InvitationAcceptedSuccessfully
):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_200_OK,
    )


async def invite_rejected_successfully_handler(
    _: Request, exc: InviteRejectedSuccessfully
):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_200_OK,
    )


async def invite_already_rejected_handler(
    _: Request, exc: InvalidInviteAlreadyRejectedError
):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_409_CONFLICT,
    )
