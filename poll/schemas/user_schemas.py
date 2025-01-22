import re
from typing import List

from fastapi import Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, field_validator
from typing_extensions import Annotated, Doc

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")


def validate_name(name: str) -> str:
    data_pattern = r"^[^\d^Ы^ы^Ё^ё^Э^э\W']+$"
    if not re.match(data_pattern, name):
        raise ValueError(
            "First and last names can contain only letters and an apostrophe"
        )
    return name.title()


class UserSchema(BaseModel):
    id: int | None = None
    first_name: str
    last_name: str
    email: str
    password: str

    class Config:
        orm_mode = True


class SignInReq(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int


class SignUpReq(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    @field_validator("first_name", "last_name", mode="before", check_fields=False)
    def _validate_names(cls, v):
        return validate_name(v)


class UserUpdateRes(BaseModel):
    first_name: str
    last_name: str

    @field_validator("first_name", "last_name", mode="before", check_fields=False)
    def _validate_names(cls, v):
        return validate_name(v)


class UsersListRes(BaseModel):
    users: List[UserSchema]


class UserDetailRes(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class Auth(OAuth2PasswordRequestForm):

    def __init__(
        self,
        *,
        username: Annotated[
            str,
            Form(),
            Doc(
                """
                                `username` string. The OAuth2 spec requires the exact field name
                                `username`.
                                """
            ),
        ],
        password: Annotated[
            str,
            Form(),
            Doc(
                """
                                `password` string. The OAuth2 spec requires the exact field name
                                `password".
                                """
            ),
        ]
    ):
        super().__init__(
            grant_type=None,
            username=username,
            password=password,
            scope="",
            client_id=None,
            client_secret=None,
        )
