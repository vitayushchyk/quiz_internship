from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK

health_check_router = APIRouter()


@health_check_router.get("/", tags=["check"])
async def _health_check():
    return JSONResponse(
        status_code=HTTP_200_OK, content=dict(detail="ok", result="working")
    )
