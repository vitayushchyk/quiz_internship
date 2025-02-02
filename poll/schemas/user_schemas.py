import re

from fastapi import Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator
from typing_extensions import Annotated, Doc

from poll.services.exc.base_exc import InvalidEmailError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")


def validate_name(name: str) -> str:
    data_pattern = r"^[^\d^Ы^ы^Ё^ё^Э^э\W']+$"
    if not re.match(data_pattern, name):
        raise ValueError(
            "First and last names can contain only letters and an apostrophe"
        )
    return name.title()


def validate_email_field(email: str) -> str:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        raise InvalidEmailError(email)
    return email


class UserSchema(BaseModel):
    id: int | None = None
    first_name: str
    last_name: str
    email: str
    password: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int


class SignUpReq(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

    @field_validator("email", mode="before", check_fields=False)
    def _validate_email(cls, v):
        return validate_email_field(v)


class UserUpdateRes(BaseModel):
    first_name: str
    last_name: str

    @field_validator("first_name", "last_name", mode="before", check_fields=False)
    def _validate_names(cls, v):
        return validate_name(v)


class UserDetailRes(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class UserRoleRes(BaseModel):
    role: str
    company_id: int
    user_id: int


class AdminRes(BaseModel):
    company_id: int
    user_id: int
    role: str


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
