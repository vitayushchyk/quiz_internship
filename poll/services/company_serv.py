from poll.db.model_company import Company, CompanyRepository
from poll.schemas.company_schemas import (
    CompanyVisibilityReq,
    CreateCompanyReq,
    UpdateCompanyReq,
)
from poll.services.exc.company_exc import CompanyNotFoundByID


class CompanyCRUD:
    def __init__(self, company_repo: CompanyRepository):
        self.company_repo = company_repo

    async def get_all_companies(self, page: int = 1, page_size: int = 10):
        return await self.company_repo.get_all_companies(page, page_size)

    async def get_company_by_id(self, company_id: int):
        if not await self.company_repo.get_company_by_id(company_id):
            raise CompanyNotFoundByID(company_id)
        return await self.company_repo.get_company_by_id(company_id)

    async def create_new_company(self, req_data: CreateCompanyReq) -> Company:
        return await self.company_repo.create_new_company(req_data)

    async def update_company(
        self, company_id: int, user_id: int, req_data: UpdateCompanyReq
    ) -> Company:
        return await self.company_repo.update_company(company_id, user_id, req_data)

    async def delete_company(self, company_id: int, user_id: int) -> None:
        return await self.company_repo.delete_company(company_id, user_id)

    async def change_company_visibility(
        self, company_id: int, user_id: int, status: CompanyVisibilityReq
    ) -> Company:
        return await self.company_repo.change_company_visibility(
            company_id, user_id, status
        )
