from poll.db.model_company import CompanyRepository
from poll.services.exc.company_exc import CompanyNotFound


class CompanyCRUD:
    def __init__(self, company_repo: CompanyRepository):
        self.company_repo = company_repo

    async def get_all_companies(self, page: int = 1, page_size: int = 10):
        return await self.company_repo.get_all_companies(page, page_size)

    async def get_company_by_id(self, company_id: int):
        if not await self.company_repo.get_company_by_id(company_id):
            raise CompanyNotFound(company_id)
        return await self.company_repo.get_company_by_id(company_id)
