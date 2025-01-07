from pydantic import BaseModel


class CompanySchema(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int


class CompanyDetailRes(BaseModel):
    id: int | None = None
    name: str
    description: str
    owner_id: int
