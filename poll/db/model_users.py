import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from poll.db.connection import Base


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, nullable=False)
    first_name: str = Column(String)
    last_name: str = Column(String)
    email: str = Column(String, unique=True, nullable=False)
    password: str = Column(String, nullable=False)
    is_active: bool = Column(Boolean, default=False, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    created_at: datetime.date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
