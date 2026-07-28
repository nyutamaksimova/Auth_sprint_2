from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.messages import ES_UNAVAILABLE


async def elastic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=503,
        content={'detail': ES_UNAVAILABLE},
    )
