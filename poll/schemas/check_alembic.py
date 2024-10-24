from typing import Optional

from sqlmodel import Field, SQLModel


# ToDo(Vita): this model for test alembic migration. delete it when real model will be added
class TestUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None
