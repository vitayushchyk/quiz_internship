class CompanyNotFound(Exception):
    def __init__(self, company_id: int):
        self.detail = f"Company with ID {company_id} not found."
