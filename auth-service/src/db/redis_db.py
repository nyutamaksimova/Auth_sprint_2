from redis.asyncio import Redis
from fastapi import Request


async def get_redis(request: Request) -> Redis:
    return request.app.state.redis


REFRESH_PREFIX = "refresh:"
BLACKLIST_PREFIX = "blacklist:"
