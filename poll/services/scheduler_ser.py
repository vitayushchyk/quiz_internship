from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from poll.db.model_notification import NotificationStatus
from poll.services.notification_ser import NotificationCRUD
from poll.services.quiz_serv import QuizCRUD


class SchedulerService:
    def __init__(self, quiz_service: QuizCRUD, notification_service: NotificationCRUD):
        self.quiz_service = quiz_service
        self.notification_service = notification_service
        self.scheduler = AsyncIOScheduler()

    async def check_pending_tests(self):
        now = datetime.now(timezone.utc)
        one_day_ago = now - timedelta(hours=24)
        last_attempts = await self.quiz_service.get_last_attempts_for_all_users()

        for attempt in last_attempts:
            user_id = attempt.user_id
            quiz_id = attempt.quiz_id
            last_attempt = attempt.last_attempt

            if last_attempt < one_day_ago:
                notification_text = f"You need to re-run the quiz {quiz_id}."
                await self.notification_service.create_notification(
                    user_id=user_id,
                    text=notification_text,
                    status=NotificationStatus.NEW,
                )

    def setup_tasks(self):
        self.scheduler.add_job(
            self.check_pending_tests,
            trigger=CronTrigger(hour=0, minute=0, second=0, timezone=timezone.utc),
        )
        self.scheduler.start()
