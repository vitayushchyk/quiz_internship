from poll.db.model_users import UniqueViolation, UserRepository
from poll.schemas.users import SignUpReq, UserUpdateRes
from poll.services.exc.user import UserAlreadyExist, UserNotFound
from poll.services.password_hasher import PasswordHasher


class UserCRUD:
    def __init__(self, user_repository: UserRepository, hasher: PasswordHasher = None):
        self.user_repository = user_repository
        self.hasher = hasher

    async def get_all_users(self, page: int = 1, page_size: int = 10):
        return await self.user_repository.get_all_users(page, page_size)

    async def get_user_by_id(self, user_id: int):
        if not await self.user_repository.get_user_by_id(user_id):
            raise UserNotFound(user_id)
        return await self.user_repository.get_user_by_id(user_id)

    async def create_user(self, user: SignUpReq):
        try:
            user.password = self.hasher.hash_password(user.password)
            return await self.user_repository.create_user(user)
        except UniqueViolation:
            raise UserAlreadyExist(user.email)

    async def update_user(self, user_id: int, user_update: UserUpdateRes):
        user = await self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise UserNotFound(user_id)
        return await self.user_repository.update_user(user, user_update)

    async def delete_user(self, user_id: int):
        if not await self.user_repository.get_user_by_id(user_id):
            raise UserNotFound(user_id)
        await self.user_repository.delete_user(user_id)
