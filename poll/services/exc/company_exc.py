class CompanyNotFoundByID(Exception):
    def __init__(self, company_id: int):
        self.detail = f"Company with ID {company_id} not found."


class UnauthorizedCompanyAccess(Exception):
    def __init__(self, company_id: int):
        self.detail = (
            f"You do not have permission to access company with ID {company_id}."
        )


class CompanyAlreadyExist(Exception):
    def __init__(self, company_name: str):
        self.detail = f"Company with name {company_name} already exists."


class CompanyStatusNotValid(Exception):
    def __init__(self, company_status: str, valid_statuses: list):
        self.detail = (
            f"Company status '{company_status}' is not valid. "
            f"Available statuses are: {', '.join(valid_statuses)}."
        )
