from uuid import UUID
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import decode_token
from src.db.postgres import get_db
from src.db.redis_db import BLACKLIST_PREFIX
from src.db.redis_db import get_redis
from src.models.auth import CurrentUser
from src.services.db_user_service import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis)
) -> CurrentUser:
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(401, "Invalid token")

    jti = payload.get("jti")

    revoked = await redis.exists(
        BLACKLIST_PREFIX + jti
    )

    if revoked:
        raise HTTPException(
            status_code=401,
            detail="Token revoked",
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(401, "Invalid token")

    repository = UserRepository(db)

    user = await repository.get_by_id(UUID(user_id))

    if user is None:
        raise HTTPException(401, "User not found")

    return CurrentUser(
        user=user,
        payload=payload,
    )
