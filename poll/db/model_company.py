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
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from poll.db.connection import Base
from poll.schemas.company_schemas import (
    CompanyVisibilityReq,
    CreateCompanyReq,
    UpdateCompanyReq,
)
from poll.services.exc.base_exc import (
    CompanyAlreadyExist,
    CompanyNotFoundByID,
    CompanyStatusNotValid,
    UnauthorizedCompanyAccess,
    UserAlreadyMemberError,
)
from poll.services.pagination import Pagination

logger = getLogger(__name__)


class ChangeVisibility(str, Enum):
    HIDDEN = "hidden"
    VISIBLE = "visible"


class CompanyRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Company(Base):
    __tablename__ = "companies"

    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(String(100), unique=True, nullable=False)
    description: str = Column(String(256), nullable=False)
    status: ChangeVisibility = Column(
        ENUM(ChangeVisibility, name="company_status_change"),
        nullable=False,
        default=ChangeVisibility.VISIBLE,
    )
    owner_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: datetime.date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime.date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    owner = relationship("User", back_populates="companies", cascade="all, delete")
    company_user_roles = relationship(
        "CompanyUserRole", back_populates="company", cascade="all, delete"
    )


class CompanyUserRole(Base):
    __tablename__ = "company_user_roles"
    id: int = Column(Integer, primary_key=True, nullable=False)
    company_id: int = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    role: CompanyRole = Column(
        ENUM(CompanyRole, name="company_user_role"),
        nullable=False,
    )
    created_at: datetime.date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime.date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    company = relationship("Company", back_populates="company_user_roles")
    user = relationship("User", back_populates="role_in_companies")

    __table_args__ = (
        UniqueConstraint(
            "company_id", "user_id", "role", name="unique_company_user_role"
        ),
    )


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_companies(
        self, page: int = 1, page_size: int = 10
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        logger.info(f"Fetching all companies (page: {page}, page_size: {page_size})")
        paginator = Pagination(self.session, select(Company), page, page_size)
        paginate_companies = await paginator.fetch_results()
        return paginate_companies

    async def get_company_by_id(self, company_id: int) -> Company | None:
        logger.info(f"Fetching company by ID: {company_id}")
        query = select(Company).filter(Company.id == company_id)
        return (await self.session.execute(query)).scalar()

    async def create_new_company(self, req_data: CreateCompanyReq) -> Company:
        logger.info(f"Creating new company: {req_data}")

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

        owner_role = CompanyUserRole(
            company_id=new_company.id, user_id=req_data.owner_id, role=CompanyRole.OWNER
        )
        self.session.add(owner_role)
        await self.session.commit()

        return new_company

    async def update_company(
        self, company_id: int, user_id: int, req_data: UpdateCompanyReq
    ) -> Company:
        logger.info(f"Updating company: {req_data}")

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
        logger.info(f"Deleting company: {company_id}")
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
        logger.info(f"Changing company visibility: {status}")

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

    async def get_user_role(
        self, company_id: int, user_id: int
    ) -> CompanyUserRole | None:
        logger.info(f"Getting user role: {company_id} {user_id}")
        query = select(CompanyUserRole).filter(
            CompanyUserRole.company_id == company_id, CompanyUserRole.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def add_user_to_company(
        self, company_id: int, user_id: int, role: CompanyRole
    ) -> CompanyUserRole:
        logger.info(f"Adding user to company: {company_id} {user_id} {role}")
        new_role = CompanyUserRole(company_id=company_id, user_id=user_id, role=role)
        self.session.add(new_role)

        try:
            await self.session.commit()
            await self.session.refresh(new_role)
            return new_role
        except IntegrityError as e:
            await self.session.rollback()
            if "unique_company_user_role" in str(e.orig):
                raise UserAlreadyMemberError(
                    company_id=company_id, user_id=user_id, role=role.value
                )
            raise

    async def delete_user_from_company(self, company_id: int, user_id: int) -> None:
        logger.info(f"Deleting user from company: {company_id} {user_id}")
        query = select(CompanyUserRole).filter(
            CompanyUserRole.company_id == company_id, CompanyUserRole.user_id == user_id
        )
        result = await self.session.execute(query)
        role = result.scalar()
        if role:
            await self.session.delete(role)
            await self.session.commit()
