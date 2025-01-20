from poll.db.model_company import CompanyRepository, logger
from poll.db.model_invite import InviteRepository
from poll.db.model_users import UserRepository
from poll.services.exc.company_exc import CompanyNotFoundByID
from poll.services.exc.invite_exc import (
    InvitationAlreadyExistError,
    InvitationNotExistsError,
    PermissionDeniedError,
)
from poll.services.exc.user import UserNotFound


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

    async def owner_send_invite(
        self, company_id: int, user_id: int, current_user_id: int
    ):
        logger.info(
            f"Checking if current_user_id={current_user_id} is the owner of company_id={company_id}..."
        )
        is_owner = await self.company_repo.check_owner(company_id, current_user_id)
        if not is_owner:
            raise PermissionDeniedError
        logger.info(f"Checking if company with ID {company_id} exists...")
        check_company = await self.company_repo.get_company_by_id(company_id)
        if not check_company:
            raise CompanyNotFoundByID(company_id)

        logger.info(f"Checking if user with ID {user_id} exists...")
        check_user = await self.user_repo.get_user_by_id(user_id)
        if not check_user:
            raise UserNotFound(user_id)
        existing_invite = await self.invite_repo.get_invite_by_id(
            company_id=company_id, user_id=user_id
        )
        if existing_invite:
            raise InvitationAlreadyExistError(user_id)

        logger.info(
            f"Creating invite for company_id={company_id} and user_id={user_id}..."
        )

        return await self.invite_repo.add_invite(company_id=company_id, user_id=user_id)

    async def owner_cancel_invite(
        self, company_id: int, user_id: int, current_user_id: int
    ):
        logger.info(
            f"Trying to cancel invite for user_id={user_id} in company_id={company_id} by current_user_id={current_user_id}"
        )

        logger.info(f"Verifying ownership for company_id={company_id}...")
        is_owner = await self.company_repo.check_owner(company_id, current_user_id)
        if not is_owner:

            raise PermissionDeniedError

        logger.info(
            f"Checking if invite exists for user_id={user_id} in company_id={company_id}..."
        )
        invite = await self.invite_repo.get_invite_by_id(
            company_id=company_id, user_id=user_id
        )
        if not invite:
            raise InvitationNotExistsError

        logger.info(
            f"Deleting invite for user_id={user_id} in company_id={company_id}..."
        )
        await self.invite_repo.delete_invite(company_id=company_id, user_id=user_id)
        return
