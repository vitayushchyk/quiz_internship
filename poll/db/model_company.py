import datetime
from enum import Enum
from logging import getLogger
from typing import Any, Sequence

from sqlalchemy import (
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
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from poll.db.connection import Base
from poll.schemas.company_schemas import (
    CompanyVisibilityReq,
    CreateCompanyReq,
    UpdateCompanyReq,
)
from poll.services.exc.company_exc import (
    CompanyAlreadyExist,
    CompanyNotFoundByID,
    CompanyStatusNotValid,
    UnauthorizedCompanyAccess,
)
from poll.services.pagination import Pagination

logger = getLogger(__name__)


class ChangeVisibility(str, Enum):
    HIDDEN = "hidden"
    VISIBLE = "visible"


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    status = Column(
        ENUM(ChangeVisibility, name="company_status_change"),
        nullable=False,
        default=ChangeVisibility.VISIBLE,
    )
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

    async def create_new_company(self, req_data: CreateCompanyReq) -> Company:
        logger.info("Creating company: %s", req_data)
        existing_company = await self.session.execute(
            select(Company).where(Company.name == req_data.name)
        )
        existing_company = existing_company.scalars().first()
        if existing_company:
            raise CompanyAlreadyExist(company_name=existing_company.name)
        new_company = Company(
            name=req_data.name,
            description=req_data.description,
            owner_id=req_data.owner_id,
        )
        self.session.add(new_company)
        await self.session.commit()
        await self.session.refresh(new_company)
        return new_company

    async def update_company(
        self, company_id: int, user_id: int, req_data: UpdateCompanyReq
    ) -> Company:
        logger.info("Updating company: %s", req_data)

        query = select(Company).filter(Company.id == company_id)
        company = (await self.session.execute(query)).scalar()

        if not company:
            raise CompanyNotFoundByID(company_id)

        if company.owner_id != user_id:
            raise UnauthorizedCompanyAccess(company_id)

        if req_data.name is not None:
            company.name = req_data.name
        if req_data.description is not None:
            company.description = req_data.description

        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)
        return company

    async def delete_company(self, company_id: int, user_id: int) -> None:
        logger.info("Deleting company: %s", company_id)
        query = select(Company).filter(Company.id == company_id)
        company = (await self.session.execute(query)).scalar()
        if not company:
            raise CompanyNotFoundByID(company_id)
        if company.owner_id != user_id:
            raise UnauthorizedCompanyAccess(company_id)
        await self.session.delete(company)
        await self.session.commit()

    async def change_company_visibility(
        self, company_id: int, user_id: int, status: CompanyVisibilityReq
    ) -> Company:
        logger.info("Changing company visibility: %s", status)

        query = select(Company).filter(Company.id == company_id)
        company = (await self.session.execute(query)).scalar()

        if not company:
            raise CompanyNotFoundByID(company_id)

        if company.owner_id != user_id:
            raise UnauthorizedCompanyAccess(company_id)

        if status.status not in [ChangeVisibility.HIDDEN, ChangeVisibility.VISIBLE]:
            valid_statuses = [status for status in ChangeVisibility]
            raise CompanyStatusNotValid(
                company_status=status.status, valid_statuses=valid_statuses
            )

        company.status = status.status
        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)

        return company
