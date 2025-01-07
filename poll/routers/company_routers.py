from typing import List

from fastapi import APIRouter, status
from fastapi.params import Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from poll.core.deps import get_company_repository
from poll.schemas.company_schemas import CompanyDetailRes
from poll.services.company_serv import CompanyCRUD
from poll.services.exc.company_exc import CompanyNotFound

company_router = APIRouter(prefix="/company", tags=["company"])


@company_router.get(
    "/list/", summary="List all companies", response_model=List[CompanyDetailRes]
)
async def companies_list(
    page: int = 1, company_service: CompanyCRUD = Depends(get_company_repository)
):
    return await company_service.get_all_companies(page=page)


@company_router.get("/{company_id}/", summary="Get company by id")
async def company_by_id(
    company_id: int, company_service: CompanyCRUD = Depends(get_company_repository)
):
    return await company_service.get_company_by_id(company_id)


async def company_not_found_handler(_: Request, exc: CompanyNotFound):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_404_NOT_FOUND,
    )
