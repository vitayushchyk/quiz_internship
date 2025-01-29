from typing import List

from fastapi import APIRouter, Depends
from starlette import status

from poll.core.deps import get_current_user, get_current_user_id, get_invite_crud
from poll.db.model_users import User
from poll.schemas.invite_schemas import InviteRes, InviteStatusRequest
from poll.services.invite_serv import InviteCRUD

invite_router = APIRouter(prefix="/invite", tags=["Invite"])


@invite_router.post(
    "/",
    response_model=InviteRes,
    status_code=status.HTTP_201_CREATED,
    summary="The owner sends an invitation",
    description="The company owner sends the user an invitation to join the company.",
)
async def send_invite_to_user(
    company_id: int,
    target_user_id: int,
    current_user: User = Depends(get_current_user),
    invite_crud: InviteCRUD = Depends(get_invite_crud),
):
    invite = await invite_crud.owner_send_invite(
        company_id=company_id,
        target_user_id=target_user_id,
        current_user_id=current_user.id,
    )
    return invite


@invite_router.put(
    "/owner/{company_id}/{invite_id}/{status}/",
    summary="The owner updates the status of the invitation",
    description="The company owner updates the status of the invitation for the user (accept/reject).",
    status_code=status.HTTP_200_OK,
)
async def user_response_to_invite_route(
    company_id: int,
    invite_id: int,
    new_status: InviteStatusRequest,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    return await invite_service.owner_update_invite_status(
        company_id=company_id,
        invite_id=invite_id,
        new_status=new_status.invite_status,
        current_user_id=current_user_id,
    )


@invite_router.delete(
    "/owner/decline/invite/{company_id}/user/{user_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="The owner cancels an invite",
    description="The company owner cancels the invitation sent to a user.",
)
async def decline_invite_to_user(
    company_id: int,
    target_user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    await invite_service.owner_cancel_invite(
        company_id=company_id,
        target_user_id=target_user_id,
        current_user_id=current_user_id,
    )


@invite_router.delete(
    "/owner/remove/{company_id}/user/{user_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="The owner removes a user from the company",
    description="The company owner removes a user from the company.",
)
async def remove_user_from_company(
    company_id: int,
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    await invite_service.owner_remove_user(
        company_id=company_id, target_user_id=user_id, current_user_id=current_user_id
    )


@invite_router.get(
    "/invites/list/",
    response_model=List[InviteRes],
    summary="Get invites with status PENDING for the current user.",
    description="Returns list of all invites with status PENDING for the current user.",
)
async def read_user_invites(
    user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    return await invite_service.user_show_invites(user_id=user_id)


@invite_router.post(
    "/request/{company_id}/",
    status_code=status.HTTP_201_CREATED,
    response_model=InviteRes,
    summary="User sends a join request",
    description="User sends a join request for the company.",
)
async def send_join_request(
    company_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    return await invite_service.user_send_join_request(
        company_id=company_id, current_user_id=current_user_id
    )


@invite_router.put(
    "/{company_id}/invites/",
    summary="User updates their invitation status",
    description="User updates their invitation status (accept/reject).",
    status_code=status.HTTP_200_OK,
)
async def user_response_to_invite_route(
    company_id: int,
    invite_id: int,
    new_status: InviteStatusRequest,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    return await invite_service.user_update_invite_status(
        company_id=company_id,
        invite_id=invite_id,
        new_status=new_status.invite_status,
        current_user_id=current_user_id,
    )


@invite_router.delete(
    "/user/decline/request/{company_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User cancels their join request",
    description="User cancels their join request for the company.",
)
async def cancel_join_request(
    company_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    await invite_service.user_cancel_join_request(
        company_id=company_id, current_user_id=current_user_id
    )


@invite_router.delete(
    "/user/leave/{company_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User leaves the company",
)
async def user_leave_company(
    company_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    await invite_service.user_leave_company(
        company_id=company_id, current_user_id=current_user_id
    )
