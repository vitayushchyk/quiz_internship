class CompanyNotFoundByID(Exception):
    def __init__(self, company_id: int):
        self.detail = f"Company with ID {company_id} not found."


class UnauthorizedCompanyAccess(Exception):
    def __init__(self, company_id: int):
        self.detail = (
            f"You do not have permission to access company with ID {company_id}."
        )
