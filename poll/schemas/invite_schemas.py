from pydantic import BaseModel, field_validator

from poll.db.model_invite import InviteStatus
from poll.services.exc.base_exc import InvalidActionError


class InviteRes(BaseModel):
    id: int
    company_id: int
    user_id: int
    invite_status: InviteStatus

    class Config:
        orm_mode = True


class InviteStatusRequest(BaseModel):
    invite_status: InviteStatus

    @field_validator("invite_status")
    def validate_only_accepted_or_rejected(cls, value: InviteStatus):
        if value not in {InviteStatus.ACCEPTED, InviteStatus.REJECTED}:
            raise InvalidActionError(status=value)
        return value
