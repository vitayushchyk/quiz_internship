from typing import List

from fastapi import APIRouter, Depends
from requests import Request
from starlette import status
from starlette.responses import JSONResponse

from poll.core.deps import get_current_user_id, get_invite_crud
from poll.db.model_invite import InviteStatus, logger
from poll.schemas.invite_schemas import InviteCreateReq, InviteRes, InviteUserReq
from poll.services.exc.company_exc import CompanyNotFoundByID
from poll.services.exc.invite_exc import (
    CannotInviteYourselfError,
    DeniedUserError,
    InvalidActionError,
    InvalidInvitationAlreadyRejectedError,
    InvitationAcceptedSuccessfully,
    InvitationAlreadyExistError,
    InvitationNotExistsError,
    InvitationRejectedSuccessfully,
    PermissionDeniedError,
)
from poll.services.exc.user_exc import UserNotFound
from poll.services.invite_serv import InviteCRUD

invite_router = APIRouter(prefix="/invite", tags=["Invite"])


@invite_router.post(
    "/",
    response_model=InviteRes,
    status_code=status.HTTP_201_CREATED,
    summary="Owner creates an invite",
)
async def create_invite_to_user(
    request: InviteCreateReq,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    return await invite_service.owner_send_invite(
        company_id=request.company_id,
        user_id=request.user_id,
        current_user_id=current_user_id,
    )


@invite_router.delete(
    "/{company_id}/{user_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Owner cancels an invite",
)
async def cancel_invite_to_user(
    company_id: int,
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    await invite_service.owner_cancel_invite(
        company_id=company_id, user_id=user_id, current_user_id=current_user_id
    )


@invite_router.put(
    "/{company_id}/requests/{invite_id}/{action}/",
    summary="Owner Change user's join request status (accept/reject)",
    response_model=InviteRes,
)
async def owner_update_invite_status(
    company_id: int,
    invite_id: int,
    action: str,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    logger.info(
        f"Owner {current_user_id} attempting to change invite {invite_id} for company {company_id} with action {action}"
    )
    await invite_service._check_owner_or_raise(company_id, current_user_id)
    if action == "accept":
        new_status = InviteStatus.ACCEPTED
    elif action == "reject":
        new_status = InviteStatus.REJECTED
    else:
        raise InvalidActionError(action)
    updated_invite = await invite_service._validate_and_update_status(
        invite_id=invite_id,
        new_status=new_status,
        current_user_id=current_user_id,
        is_owner=True,
    )

    return updated_invite


@invite_router.put(
    "/{invite_id}/{action}/",
    summary="User Change invite status (accept/reject)",
    response_model=InviteRes,
)
async def update_invite_status(
    invite_id: int,
    action: str,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    if action == "accept":
        return await invite_service.user_accept_invite(
            invite_id=invite_id, current_user_id=current_user_id
        )
    elif action == "reject":
        return await invite_service.user_reject_invite(
            invite_id=invite_id, current_user_id=current_user_id
        )
    else:
        raise InvalidActionError(action=action)


@invite_router.get(
    "/invites/list/",
    response_model=List[InviteRes],
    summary="Get all invites for the current user",
)
async def read_user_invites(
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    return await invite_service.show_user_invites(current_user_id=current_user_id)


@invite_router.post(
    "/join/request/",
    response_model=InviteRes,
    summary="User submits a join request to a company",
)
async def create_join_request(
    request: InviteUserReq,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    return await invite_service.user_send_join_request(
        company_id=request.company_id, current_user_id=current_user_id
    )


@invite_router.delete(
    "/join/request/{company_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User cancels their join request",
)
async def cancel_join_request(
    company_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    await invite_service.user_cancel_join_request(
        company_id=company_id, current_user_id=current_user_id
    )


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


async def denied_action_handler(_: Request, exc: DeniedUserError):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_403_FORBIDDEN,
    )


async def invite_accepted_successfully_handler(
    _: Request, exc: InvitationAcceptedSuccessfully
):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_200_OK,
    )


async def invite_rejected_successfully_handler(
    _: Request, exc: InvitationRejectedSuccessfully
):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_200_OK,
    )


async def invite_already_rejected_handler(
    _: Request, exc: InvalidInvitationAlreadyRejectedError
):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_409_CONFLICT,
    )


async def cannot_invite_yourself_handler(_: Request, exc: CannotInviteYourselfError):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_400_BAD_REQUEST,
    )


async def invalid_action_handler(_: Request, exc: InvalidActionError):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_400_BAD_REQUEST,
    )
