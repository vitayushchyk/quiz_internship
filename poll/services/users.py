from poll.db.model_users import UserRepository
from poll.schemas.users import SignUpReq, UserUpdateRes


class UserCRUD:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_all_users(self, page: int = 1, page_size: int = 10):
        return await self.user_repository.get_all_users(page, page_size)

    async def get_user_by_id(self, user_id: int):
        return await self.user_repository.get_user_by_id(user_id)

    async def create_user(self, user: SignUpReq):
        return await self.user_repository.create_user(user)

    async def update_user(self, user_id: int, user_update: UserUpdateRes):
        return await self.user_repository.update_user(user_id, user_update)

    async def delete_user(self, user_id: int):
        await self.user_repository.delete_user(user_id)
