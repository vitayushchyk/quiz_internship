from pydantic import BaseModel


class MembershipDetail(BaseModel):
    company_id: int
    user_id: int
    status: str
