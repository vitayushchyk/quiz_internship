import jwt
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer

from poll.db.model_users import UniqueViolation, User, UserRepository
from poll.schemas.users import SignUpReq, TokenData, UserUpdateRes
from poll.services.auth_serv import decode_token
from poll.services.exc.auth import JWTTokenInvalid
from poll.services.exc.user import UserAlreadyExist, UserNotAuthenticated, UserNotFound
from poll.services.password_hasher import PasswordHasher

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")


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

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.user_repository.get_user_by_email(email)
        if user and self.hasher.verify_password(password, user.password):
            return user
        return None

    async def create_user(self, user: SignUpReq):
        try:
            user.password = self.hasher.hash_password(user.password)
            return await self.user_repository.create_user(user)
        except UniqueViolation:
            raise UserAlreadyExist(str(user.email))

    async def update_user(self, user_id: int, user_update: UserUpdateRes):
        user = await self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise UserNotFound(user_id)
        return await self.user_repository.update_user(user, user_update)

    async def delete_user(self, user_id: int):
        if not await self.user_repository.get_user_by_id(user_id):
            raise UserNotFound(user_id)
        await self.user_repository.delete_user(user_id)

    async def get_current_user(self, jwt_token: str) -> User | None:
        try:
            payload = decode_token(jwt_token)
            user_id: int = payload.get("sub")
            if user_id is None:
                raise UserNotAuthenticated
            token_data = TokenData(user_id=user_id)
        except (jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError) as e:
            raise JWTTokenInvalid from e
        user = await self.user_repository.get_user_by_id(token_data.user_id)
        return user
