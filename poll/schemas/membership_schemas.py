from pydantic import BaseModel


class InviteSuccessRes(BaseModel):
    company_id: int
    user_id: int
    membership_status: str


class InvitationStatusDetailRes(BaseModel):
    company_id: int
    user_id: int
    membership_status: str
