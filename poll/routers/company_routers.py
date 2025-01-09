from typing import List

from fastapi import APIRouter, status
from fastapi.params import Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from poll.core.deps import get_company_repository, get_current_user_id
from poll.schemas.company_schemas import (
    CompanyDetailRes,
    CompanyVisibilityReq,
    CreateCompanyReq,
    UpdateCompanyReq,
)
from poll.services.company_serv import CompanyCRUD
from poll.services.exc.company_exc import (
    CompanyAlreadyExist,
    CompanyNotFoundByID,
    CompanyStatusNotValid,
    UnauthorizedCompanyAccess,
)

company_router = APIRouter(prefix="/company", tags=["company"])


@company_router.get(
    "/list/",
    summary="List all companies",
    response_model=List[CompanyDetailRes],
)
async def companies_list(
    page: int = 1, company_service: CompanyCRUD = Depends(get_company_repository)
):
    return await company_service.get_all_companies(page=page, page_size=10)


@company_router.get(
    "/{company_id}/",
    summary="Get company by id",
)
async def company_by_id(
    company_id: int,
    company_service: CompanyCRUD = Depends(get_company_repository),
):
    return await company_service.get_company_by_id(company_id)


@company_router.post(
    "/create/",
    summary="Create a new company",
    response_model=CreateCompanyReq,
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    company: CreateCompanyReq,
    user_id: int = Depends(get_current_user_id),
    company_service: CompanyCRUD = Depends(get_company_repository),
):
    new_company = await company_service.create_new_company(
        req_data=CreateCompanyReq(
            name=company.name,
            description=company.description,
            status=company.status,
            owner_id=user_id,
        )
    )
    return new_company


@company_router.put("/{company_id}/", summary="Update company by id")
async def update_company(
    company_id: int,
    company: UpdateCompanyReq,
    user_id: int = Depends(get_current_user_id),
    company_service: CompanyCRUD = Depends(get_company_repository),
):
    updated_company = await company_service.update_company(
        company_id=company_id,
        user_id=user_id,
        req_data=company,
    )
    return updated_company


@company_router.delete(
    "/{company_id}/",
    summary="Delete company by id",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_company(
    company_id: int,
    user_id: int = Depends(get_current_user_id),
    company_service: CompanyCRUD = Depends(get_company_repository),
):
    await company_service.delete_company(company_id=company_id, user_id=user_id)
    return


@company_router.post(
    "/change/visibility",
    summary="Change company visibility",
    response_model=CompanyDetailRes,
)
async def change_company_visibility(
    company_id: int,
    company_status: CompanyVisibilityReq,
    user_id: int = Depends(get_current_user_id),
    company_service: CompanyCRUD = Depends(get_company_repository),
):
    updated_company = await company_service.change_company_visibility(
        company_id=company_id,
        user_id=user_id,
        status=company_status,
    )
    return updated_company


async def company_not_found_by_id(_: Request, exc: CompanyNotFoundByID):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def company_permission_handler(_: Request, exc: UnauthorizedCompanyAccess):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_403_FORBIDDEN,
    )


async def company_already_exists_handler(_: Request, exc: CompanyAlreadyExist):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_409_CONFLICT,
    )


async def company_status_not_valid_handler(_: Request, exc: CompanyStatusNotValid):
    return JSONResponse(
        content={"details": exc.detail},
        status_code=status.HTTP_400_BAD_REQUEST,
    )
