from fastapi import APIRouter, Depends, status

from poll.core.deps import get_current_user, get_notification_crud
from poll.db.model_users import User
from poll.schemas.notification_schemas import NotificationDetail, NotifStatus
from poll.services.notification_ser import NotificationCRUD

notification_router = APIRouter(
    prefix="/notification",
    tags=["Notification"],
)


@notification_router.get(
    "/my/{user_id}",
    response_model=list[NotificationDetail],
    description="`Current user` get notifications",
    status_code=status.HTTP_200_OK,
)
async def get_my_notifications(
    user_id: int,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    notification: NotificationCRUD = Depends(get_notification_crud),
):
    return await notification.get_my_notifications(
        user_id=user_id, current_user=current_user.id, page=page, page_size=page_size
    )


@notification_router.put(
    "/{notification_id}/status/",
    response_model=NotifStatus,
    description="Mark notification as read",
    status_code=status.HTTP_200_OK,
)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification: NotificationCRUD = Depends(get_notification_crud),
):
    return await notification.read_notification(
        notification_id=notification_id,
        current_user=current_user.id,
    )
