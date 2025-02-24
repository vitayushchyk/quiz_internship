from typing import List

from poll.db.model_company import CompanyRole
from poll.db.model_invite import InviteStatus
from poll.schemas.invite_schemas import InviteRes, InviteStatusRequest
from poll.schemas.user_schemas import AdminRes, UserRoleRes
from poll.services.exc.base_exc import (
    CannotDeleteYourselfError,
    CannotInviteYourselfError,
    CompanyNotFoundByID,
    InvalidActionError,
    InvitationActionSuccess,
    InvitationAlreadyExist,
    InvitationNotExistsError,
    PermissionDeniedError,
    PermissionUserError,
    UserAlreadyMemberError,
    UserNotFound,
    UserNotMemberError,
)


class InviteCRUD:
    def __init__(self, invite_repo, user_repo, company_repo):
        self.invite_repo = invite_repo
        self.user_repo = user_repo
        self.company_repo = company_repo

    async def _check_permission(
        self, company_id: int, user_id: int, required_roles: list[str]
    ):
        get_user_role = await self.company_repo.get_user_role(company_id, user_id)
        if not get_user_role or get_user_role.role not in required_roles:
            raise PermissionDeniedError(required_roles=required_roles)

    async def _validate_existing_membership_and_invite(
        self, company_id: int, user_id: int
    ):
        is_user_role_exist = await self.company_repo.get_user_role(
            company_id=company_id, user_id=user_id
        )
        if is_user_role_exist:
            raise UserAlreadyMemberError(
                company_id=company_id, user_id=user_id, role=is_user_role_exist.role
            )

        existing_invite = await self.invite_repo.get_invite(
            company_id=company_id, user_id=user_id
        )
        if existing_invite:
            raise InvitationAlreadyExist()

    async def _process_invite_status_update(
        self, company_id: int, invite_id: int, new_status: InviteStatus
    ):
        is_company_exist = await self.company_repo.get_company_by_id(company_id)
        if not is_company_exist:
            raise CompanyNotFoundByID(company_id=company_id)

        fetch_invite = await self.invite_repo.get_invite(
            invite_id=invite_id, only_one=True
        )
        if not fetch_invite:
            raise InvitationNotExistsError()

        if new_status == InviteStatus.ACCEPTED:
            await self.invite_repo.update_invite_status(
                invite_id=invite_id, new_status=InviteStatus.ACCEPTED
            )
            default_role = CompanyRole.MEMBER
            await self.company_repo.add_user_to_company(
                company_id=company_id, user_id=fetch_invite.user_id, role=default_role
            )
        elif new_status == InviteStatus.REJECTED:
            await self.invite_repo.update_invite_status(
                invite_id=invite_id, new_status=InviteStatus.REJECTED
            )
        else:
            raise InvalidActionError(status=new_status)
        return fetch_invite

    async def _get_invite_or_raise(self, company_id: int, user_id: int):
        invite = await self.invite_repo.get_invite(
            company_id=company_id, user_id=user_id
        )
        if not invite:
            raise InvitationNotExistsError()
        return invite

    async def owner_send_invite(
        self, company_id: int, target_user_id: int, current_user_id: int
    ):

        is_company_exist = await self.company_repo.get_company_by_id(company_id)
        if not is_company_exist:
            raise CompanyNotFoundByID(company_id=company_id)

        await self._check_permission(company_id, current_user_id, [CompanyRole.OWNER])
        if target_user_id == current_user_id:
            raise CannotInviteYourselfError()

        is_user_exist = await self.user_repo.get_user_by_id(user_id=target_user_id)
        if not is_user_exist:
            raise UserNotFound(user_id=target_user_id)

        await self._validate_existing_membership_and_invite(
            company_id=company_id, user_id=target_user_id
        )

        return await self.invite_repo.add_invite(
            company_id=company_id, user_id=target_user_id
        )

    async def owner_cancel_invite(
        self, company_id: int, target_user_id: int, current_user_id: int
    ):
        is_company_exist = await self.company_repo.get_company_by_id(company_id)
        if not is_company_exist:
            raise CompanyNotFoundByID(company_id=company_id)
        await self._check_permission(company_id, current_user_id, [CompanyRole.OWNER])

        is_user_exist = await self.user_repo.get_user_by_id(user_id=target_user_id)
        if not is_user_exist:
            raise UserNotFound(user_id=target_user_id)
        await self._check_permission(company_id, current_user_id, [CompanyRole.OWNER])
        await self._get_invite_or_raise(company_id=company_id, user_id=target_user_id)

        await self.invite_repo.delete_invite(
            company_id=company_id, user_id=target_user_id
        )
        return

    async def owner_update_invite_status(
        self,
        company_id: int,
        invite_id: int,
        new_status: InviteStatusRequest,
        current_user_id: int,
    ):
        await self._check_permission(
            company_id,
            current_user_id,
            [CompanyRole.OWNER],
        )

        await self._process_invite_status_update(
            company_id=company_id,
            invite_id=invite_id,
            new_status=new_status,
        )

        raise InvitationActionSuccess(status=new_status, company_id=company_id)

    async def owner_remove_user(
        self, company_id: int, target_user_id: int, current_user_id: int
    ):

        is_company_exist = await self.company_repo.get_company_by_id(company_id)
        if not is_company_exist:
            raise CompanyNotFoundByID(company_id=company_id)

        await self._check_permission(company_id, current_user_id, [CompanyRole.OWNER])

        if target_user_id == current_user_id:
            raise CannotDeleteYourselfError

        is_user_exist = await self.user_repo.get_user_by_id(user_id=target_user_id)
        if not is_user_exist:
            raise UserNotFound(user_id=target_user_id)

        is_user_member = await self.company_repo.get_user_role(
            company_id=company_id, user_id=target_user_id
        )
        if not is_user_member:
            raise UserNotMemberError()

        await self.company_repo.delete_user_from_company(
            company_id=company_id, user_id=target_user_id
        )

        return

    async def owner_assign_admin(
        self, company_id: int, target_user_id: int, current_user_id: int
    ):
        is_company_exist = await self.company_repo.get_company_by_id(company_id)
        if not is_company_exist:
            raise CompanyNotFoundByID(company_id=company_id)
        await self._check_permission(company_id, current_user_id, [CompanyRole.OWNER])
        is_user_exist = await self.user_repo.get_user_by_id(user_id=target_user_id)
        if not is_user_exist:
            raise UserNotFound(user_id=target_user_id)
        is_user_member = await self.company_repo.get_user_role(
            company_id=company_id, user_id=target_user_id
        )
        if not is_user_member:
            raise UserNotMemberError()
        await self.company_repo.update_user_role(
            company_id=company_id, user_id=target_user_id, new_role=CompanyRole.ADMIN
        )

        return UserRoleRes(
            role=CompanyRole.ADMIN, company_id=company_id, user_id=target_user_id
        )

    async def owner_remove_admin(
        self, company_id: int, target_user_id: int, current_user_id: int
    ):
        is_company_exist = await self.company_repo.get_company_by_id(company_id)
        if not is_company_exist:
            raise CompanyNotFoundByID(company_id=company_id)
        await self._check_permission(company_id, current_user_id, [CompanyRole.OWNER])
        is_user_exist = await self.user_repo.get_user_by_id(user_id=target_user_id)
        if not is_user_exist:
            raise UserNotFound(user_id=target_user_id)
        is_user_member = await self.company_repo.get_user_role(
            company_id=company_id, user_id=target_user_id
        )
        if not is_user_member:
            raise UserNotMemberError()
        await self.company_repo.update_user_role(
            company_id=company_id, user_id=target_user_id, new_role=CompanyRole.MEMBER
        )
        return UserRoleRes(
            role=CompanyRole.ADMIN, company_id=company_id, user_id=target_user_id
        )

    async def owner_get_admins(self, company_id: int, current_user_id: int):
        is_company_exist = await self.company_repo.get_company_by_id(company_id)
        if not is_company_exist:
            raise CompanyNotFoundByID(company_id=company_id)
        await self._check_permission(company_id, current_user_id, [CompanyRole.OWNER])
        admins = await self.company_repo.get_admins(
            company_id=company_id,
        )
        return [
            AdminRes(
                company_id=admin.company_id, user_id=admin.user_id, role=admin.role
            )
            for admin in admins
        ]

    async def user_show_invites(self, user_id: int) -> List[InviteRes]:
        return await self.invite_repo.get_invite(user_id=user_id)

    async def user_send_join_request(self, company_id: int, current_user_id: int):
        is_company_exist = await self.company_repo.get_company_by_id(
            company_id=company_id
        )
        if not is_company_exist:
            raise CompanyNotFoundByID(company_id=company_id)
        await self._validate_existing_membership_and_invite(
            company_id=company_id, user_id=current_user_id
        )
        return await self.invite_repo.add_invite(
            company_id=company_id, user_id=current_user_id
        )

    async def user_cancel_join_request(self, company_id: int, current_user_id: int):
        is_company_exist = await self.company_repo.get_company_by_id(
            company_id=company_id
        )
        if not is_company_exist:
            raise CompanyNotFoundByID(company_id=company_id)
        await self._get_invite_or_raise(company_id=company_id, user_id=current_user_id)
        await self.invite_repo.delete_invite(
            company_id=company_id, user_id=current_user_id
        )
        return

    async def user_update_invite_status(
        self,
        company_id: int,
        invite_id: int,
        new_status: InviteStatusRequest,
        current_user_id: int,
    ):
        invite = await self._process_invite_status_update(
            company_id=company_id,
            invite_id=invite_id,
            new_status=new_status,
        )
        if invite.user_id != current_user_id:
            raise PermissionUserError(invite_id=invite_id)

        raise InvitationActionSuccess(status=new_status, company_id=company_id)

    async def user_leave_company(self, company_id: int, current_user_id: int):
        is_company_exist = await self.company_repo.get_company_by_id(
            company_id=company_id
        )
        if not is_company_exist:
            raise CompanyNotFoundByID(company_id=company_id)
        is_user_member = await self.company_repo.get_user_role(
            company_id=company_id, user_id=current_user_id
        )
        if not is_user_member:
            raise UserNotMemberError
        await self.company_repo.delete_user_from_company(
            company_id=company_id, user_id=current_user_id
        )
        return
