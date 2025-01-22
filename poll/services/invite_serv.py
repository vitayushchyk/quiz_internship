from poll.db.model_company import CompanyRepository, logger
from poll.db.model_invite import InviteRepository, InviteStatus
from poll.db.model_users import UserRepository
from poll.services.exc.company_exc import CompanyNotFoundByID
from poll.services.exc.invite_exc import (
    CannotInviteYourselfError,
    DeniedUserError,
    InvalidInvitationAlreadyRejectedError,
    InvitationAcceptedSuccessfully,
    InvitationAlreadyAcceptedError,
    InvitationAlreadyExistError,
    InvitationNotExistsError,
    InvitationRejectedSuccessfully,
    PermissionDeniedError,
)
from poll.services.exc.user_exc import UserNotFound, UserNotMemberError


class InviteCRUD:
    def __init__(
        self,
        invite_repo: InviteRepository,
        user_repo: UserRepository,
        company_repo: CompanyRepository,
    ):
        self.invite_repo = invite_repo
        self.user_repo = user_repo
        self.company_repo = company_repo

    async def _get_invite_or_raise(
        self,
        invite_id: int = None,
        company_id: int = None,
        user_id: int = None,
    ):
        logger.info(
            f"_get_invite_or_raise: invite_id={invite_id}, company_id={company_id}, user_id={user_id}"
        )
        invite = await self.invite_repo.get_invite(
            invite_id=invite_id, company_id=company_id, user_id=user_id
        )
        if not invite:
            raise InvitationNotExistsError
        return invite

    async def _check_owner_or_raise(
        self,
        company_id: int,
        current_user_id: int,
    ):
        logger.info(
            f"_check_owner_or_raise: company_id={company_id}, current_user_id={current_user_id}"
        )
        if not await self.company_repo.check_owner(company_id, current_user_id):
            raise PermissionDeniedError

    async def _validate_and_update_status(
        self,
        invite_id: int,
        new_status: InviteStatus,
        current_user_id: int,
        is_owner: bool = False,
    ):
        invite = await self._get_invite_or_raise(invite_id=invite_id)

        logger.info(
            f"Validating update: invite_user_id={invite.user_id}, current_user_id={current_user_id}, "
            f"current_status={invite.invite_status}, new_status={new_status}, is_owner={is_owner}"
        )

        if not is_owner and invite.user_id != current_user_id:
            raise DeniedUserError()

        if invite.invite_status == new_status:
            if new_status == InviteStatus.ACCEPTED:
                raise InvitationAlreadyAcceptedError(invitation_id=invite_id)
            elif new_status == InviteStatus.REJECTED:
                raise InvalidInvitationAlreadyRejectedError(invitation_id=invite_id)

        await self.invite_repo.update_invite_status(invite_id, new_status)

        if new_status == InviteStatus.ACCEPTED:
            raise InvitationAcceptedSuccessfully(status=new_status.name)
        elif new_status == InviteStatus.REJECTED:
            raise InvitationRejectedSuccessfully(status=new_status.name)

    async def owner_send_invite(
        self,
        company_id: int,
        user_id: int,
        current_user_id: int,
    ):
        logger.info(
            f"Owner {current_user_id} sending invite to user {user_id} for company {company_id}"
        )
        await self._check_owner_or_raise(company_id, current_user_id)

        if user_id == current_user_id:
            raise CannotInviteYourselfError

        if not await self.company_repo.get_company_by_id(company_id):
            raise CompanyNotFoundByID(company_id)
        if not await self.user_repo.get_user_by_id(user_id):
            raise UserNotFound(user_id)

        if await self.invite_repo.get_invite(company_id=company_id, user_id=user_id):
            raise InvitationAlreadyExistError(user_id)

        return await self.invite_repo.add_invite(company_id=company_id, user_id=user_id)

    async def owner_cancel_invite(
        self,
        company_id: int,
        user_id: int,
        current_user_id: int,
    ):
        logger.info(
            f"Owner {current_user_id} canceling invite (company_id={company_id}, user_id={user_id})"
        )
        await self._check_owner_or_raise(company_id, current_user_id)
        invite = await self._get_invite_or_raise(company_id=company_id, user_id=user_id)
        await self.invite_repo.delete_invite(
            company_id=invite.company_id, user_id=invite.user_id
        )

    async def owner_remove_user(
        self, company_id: int, user_id: int, current_user_id: int
    ):
        logger.info(
            f"Owner {current_user_id} removing user {user_id} from company {company_id}"
        )

        await self._check_owner_or_raise(company_id, current_user_id)

        deleted = await self.invite_repo.delete_invite(
            company_id=company_id, user_id=user_id
        )
        if not deleted:
            raise UserNotMemberError()

    async def user_accept_invite(
        self,
        invite_id: int,
        current_user_id: int,
    ):
        logger.info(f"User {current_user_id} accepting invite {invite_id}")
        return await self._validate_and_update_status(
            invite_id, InviteStatus.ACCEPTED, current_user_id
        )

    async def user_reject_invite(
        self,
        invite_id: int,
        current_user_id: int,
    ):
        logger.info(f"User {current_user_id} rejecting invite {invite_id}")
        return await self._validate_and_update_status(
            invite_id, InviteStatus.REJECTED, current_user_id
        )

    async def show_user_invites(
        self,
        current_user_id: int,
    ):
        logger.info(f"Fetching invites for user {current_user_id}")
        return await self.invite_repo.get_user_invites(user_id=current_user_id)

    async def user_send_join_request(
        self,
        company_id: int,
        current_user_id: int,
    ):
        logger.info(
            f"User {current_user_id} sending join request to company {company_id}"
        )
        if await self.company_repo.check_owner(company_id, current_user_id):
            raise CannotInviteYourselfError

        if not await self.company_repo.get_company_by_id(company_id):
            raise CompanyNotFoundByID(company_id)

        if await self.invite_repo.get_invite(
            company_id=company_id, user_id=current_user_id
        ):
            raise InvitationAlreadyExistError(user_id=current_user_id)

        return await self.invite_repo.add_invite(
            company_id=company_id, user_id=current_user_id
        )

    async def user_cancel_join_request(
        self,
        company_id: int,
        current_user_id: int,
    ):
        logger.info(
            f"User {current_user_id} canceling join request for company {company_id}"
        )
        invite = await self._get_invite_or_raise(
            company_id=company_id, user_id=current_user_id
        )
        await self.invite_repo.delete_invite(
            company_id=invite.company_id, user_id=invite.user_id
        )

    async def user_leave_company(self, company_id: int, current_user_id: int):
        logger.info(f"User {current_user_id} leaving company {company_id}")
        await self.company_repo.get_company_by_id(company_id)
        if not company_id:
            raise CompanyNotFoundByID(company_id)

        leave = await self.invite_repo.delete_invite(
            company_id=company_id, user_id=current_user_id
        )
        if not leave:
            raise UserNotMemberError()
