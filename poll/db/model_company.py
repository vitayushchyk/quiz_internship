import datetime
from logging import getLogger
from typing import Any, Sequence

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Row,
    RowMapping,
    String,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from poll.db.connection import Base
from poll.services.pagination import Pagination

logger = getLogger(__name__)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_visible = Column(Boolean, default=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: datetime.date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    owner = relationship("User", back_populates="companies")


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_companies(
        self, page: int = 1, page_size: int = 10
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        logger.info("Fetching all companies (page: %s, page_size: %s)", page, page_size)
        paginator = Pagination(self.session, select(Company), page, page_size)
        paginate_companies = await paginator.fetch_results()
        return paginate_companies

    async def get_company_by_id(self, company_id: int) -> Company | None:
        logger.info("Fetching company by ID: %s", company_id)
        query = select(Company).filter(Company.id == company_id)
        return (await self.session.execute(query)).scalar()
