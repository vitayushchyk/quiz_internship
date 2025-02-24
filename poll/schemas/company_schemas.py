from pydantic import BaseModel


class CompanyDetailRes(BaseModel):
    id: int
    name: str
    description: str
    status: str
    owner_id: int


class CreateCompanyReq(BaseModel):
    name: str
    description: str
    status: str
    owner_id: int


class UpdateCompanyReq(BaseModel):
    name: str
    description: str


class CompanyVisibilityReq(BaseModel):
    status: str
