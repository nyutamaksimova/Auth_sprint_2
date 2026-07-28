from fastapi import Request
from fastapi import Depends
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate


async def rate_limit_identifier(request: Request) -> str:
    if hasattr(request.state, "user"):
        return str(request.state.user.sub)

    return request.client.host


rate_limit = Depends(
    RateLimiter(times=20, seconds=60)
)
