from sqlalchemy import Column, Integer, String

from poll.db.connection import Base


# ToDo(Vita): this model for test alembic migration. delete it when real model will be added
class TestUser(Base):
    __tablename__ = "test_user"

    id = Column(Integer, primary_key=True, nullable=True)
    name = Column(String)
    secret_name = Column(String)
    age = Column(Integer, nullable=True)
