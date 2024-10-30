from typing import List

from pydantic import BaseModel, Field

from poll.db.model_users import User


class UserSchema(BaseModel):
    id: int | None = None
    first_name: str
    last_name: str
    email: str
    password: str

    class Config:
        orm_mode = True


class SignIn(BaseModel):
    email: str
    password: str


class SignUp(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")


class UsersList(BaseModel):
    users: List[User]


class UserDetail(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
