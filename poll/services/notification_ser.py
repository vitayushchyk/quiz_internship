from poll.db.model_notification import NotificationStatus
from poll.schemas.notification_schemas import NotificationDetail, NotifStatus
from poll.services.exc.base_exc import GeneralPermissionError, ResultNotFound


class NotificationCRUD:
    def __init__(self, notification_repo):
        (self.notification_repo,) = (notification_repo,)

    async def get_my_notifications(
        self, user_id: int, current_user: int, page: int = 1, page_size: int = 10
    ):
        if current_user != user_id:
            raise GeneralPermissionError
        results = await self.notification_repo.get_notifications(
            user_id=user_id, page=page, page_size=page_size
        )

        if not results:
            raise ResultNotFound()
        return [
            NotificationDetail(
                notification_id=notif.id, text=notif.text, status=notif.status_notif
            )
            for notif in results
        ]

    async def read_notification(
        self, notification_id: int, current_user: int
    ) -> NotifStatus:

        notification = await self.notification_repo.get_new_status_notifications(
            notification_id=notification_id, user_id=current_user
        )

        if not notification:
            raise ResultNotFound()
        return NotifStatus(
            notification_id=notification.id, status=notification.status_notif
        )

    async def create_notification(
        self, user_id: int, text: str, status: NotificationStatus.NEW
    ):
        return await self.notification_repo.add_notification(
            user_id=user_id, text=text, status=status
        )
