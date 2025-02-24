from typing import List

from fastapi import APIRouter, Depends, status

from poll.core.deps import (
    get_company_repository,
    get_current_user,
    get_current_user_id,
    get_invite_crud,
)
from poll.db.model_users import User
from poll.schemas.company_schemas import (
    CompanyDetailRes,
    CompanyVisibilityReq,
    CreateCompanyReq,
    UpdateCompanyReq,
)
from poll.schemas.user_schemas import AdminRes
from poll.services.company_serv import CompanyCRUD
from poll.services.invite_serv import InviteCRUD

company_router = APIRouter(prefix="/company", tags=["Company"])


@company_router.get(
    "/",
    description="Get all companies",
    response_model=List[CompanyDetailRes],
)
async def companies_list(
    page: int = 1, company_service: CompanyCRUD = Depends(get_company_repository)
):
    return await company_service.get_all_companies(page=page, page_size=10)


@company_router.get(
    "/{company_id}/",
    description="Get company by id",
    response_model=CompanyDetailRes,
)
async def company_by_id(
    company_id: int,
    company_service: CompanyCRUD = Depends(get_company_repository),
):
    return await company_service.get_company_by_id(company_id)


@company_router.post(
    "/",
    description="Create a new company",
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


@company_router.put(
    "/{company_id}/",
    description=" `Owner` update company by id",
    response_model=CreateCompanyReq,
)
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
    description="`Owner` delete company by id",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_company(
    company_id: int,
    user_id: int = Depends(get_current_user_id),
    company_service: CompanyCRUD = Depends(get_company_repository),
):
    await company_service.delete_company(company_id=company_id, user_id=user_id)


@company_router.post(
    "/change-visibility/{company_id}/",
    status_code=status.HTTP_200_OK,
    description="`Owner` change company visibility",
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


@company_router.post(
    "/{company_id}/appoint-admin/{user_id}/",
    status_code=status.HTTP_200_OK,
    description=" `Owner` of  company to appoint administrators from the company's member list.",
)
async def assign_admin(
    company_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: InviteCRUD = Depends(get_invite_crud),
):
    return await service.owner_assign_admin(
        company_id=company_id, target_user_id=user_id, current_user_id=current_user.id
    )


@company_router.post(
    "/{company_id}/remove-admin/{user_id}/",
    status_code=status.HTTP_200_OK,
    description=" `Owner` of  company to remove administrators from the company's member list.",
)
async def remove_admin(
    company_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: InviteCRUD = Depends(get_invite_crud),
):
    return await service.owner_remove_admin(
        company_id=company_id, target_user_id=user_id, current_user_id=current_user.id
    )


@company_router.get(
    "/{company_id}/admins/", description="Get Admins", response_model=list[AdminRes]
)
async def get_admins(
    company_id: int,
    current_user: User = Depends(get_current_user),
    service: InviteCRUD = Depends(get_invite_crud),
):
    return await service.owner_get_admins(
        company_id=company_id, current_user_id=current_user.id
    )


@company_router.delete(
    "/user-leave/{company_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    description="`User` leaves the company.",
)
async def user_leave_company(
    company_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    await invite_service.user_leave_company(
        company_id=company_id, current_user_id=current_user_id
    )


@company_router.delete(
    "/owner-remove/{company_id}/user/{user_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="The owner removes a user from the company",
    description="The company `owner` removes a user from the company.",
)
async def remove_user_from_company(
    company_id: int,
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    invite_service: InviteCRUD = Depends(get_invite_crud),
):
    await invite_service.owner_remove_user(
        company_id=company_id, target_user_id=user_id, current_user_id=current_user_id
    )
