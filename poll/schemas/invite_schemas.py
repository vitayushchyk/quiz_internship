from pydantic import BaseModel

from poll.db.model_invite import InviteStatus


class InviteRes(BaseModel):
    id: int
    company_id: int
    user_id: int
    invite_status: InviteStatus

    class Config:
        orm_mode = True


class InviteCreateReq(BaseModel):
    company_id: int
    user_id: int
