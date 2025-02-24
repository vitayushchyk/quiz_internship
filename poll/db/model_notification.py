import datetime
from enum import Enum
from typing import Sequence

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    insert,
    select,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from poll.db.connection import Base


class NotificationStatus(str, Enum):
    NEW = "new"
    READ = "read"


class Notification(Base):
    __tablename__ = "notifications"

    id: int = Column(Integer, primary_key=True, nullable=False)
    user_id: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    text: str = Column(String(500), nullable=False)
    status_notif: NotificationStatus = Column(
        ENUM(NotificationStatus, name="notification_status"),
        nullable=False,
        default=NotificationStatus.NEW,
    )
    created_at: datetime.datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime.datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="notifications")


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_notifications(
        self, user_id: int, page: int = 1, page_size: int = 10
    ) -> Sequence[Notification]:
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_new_status_notifications(
        self, notification_id: int, user_id: int
    ) -> Notification | None:
        query = select(Notification).where(
            Notification.id == notification_id, Notification.user_id == user_id
        )
        result = await self.session.execute(query)
        notification = result.scalar()
        if not notification:
            return None
        notification.status_notif = NotificationStatus.READ
        await self.session.commit()

        return notification

    async def add_notification(
        self, user_id: int, text: str, status: NotificationStatus
    ):
        query = (
            insert(Notification)
            .values(
                user_id=user_id,
                text=text,
                status_notif=status,
            )
            .returning(Notification)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.fetchone()
