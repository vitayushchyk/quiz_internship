from pydantic import BaseModel

from poll.db.model_notification import NotificationStatus


class NotificationDetail(BaseModel):
    notification_id: int
    text: str
    status: NotificationStatus


class NotifStatus(BaseModel):
    notification_id: int
    status: NotificationStatus

    class Config:
        orm_mode = True
