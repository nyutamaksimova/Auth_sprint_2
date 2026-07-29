from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.postgres import get_db
from src.db.redis_db import get_redis
from src.services.oauth.resolver import get_oauth_provider
from src.services.oauth.state import OAuthStateService
from src.services.token_service import TokenService

router = APIRouter(
    prefix="/provider",
    tags=["Provider"]
)


@router.get("/{provider_name}/login")
async def login(
        provider_name: str,
        redis: Redis = Depends(get_redis),
):
    provider = get_oauth_provider(provider_name)

    oauth_state_service = OAuthStateService(redis)
    state = await oauth_state_service.create()

    return RedirectResponse(
        await provider.get_login_url(state)
    )


@router.get("/{provider_name}/callback")
async def callback(
        provider_name: str,
        code: str,
        state: str,
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
):
    oauth_state_service = OAuthStateService(redis)

    if not await oauth_state_service.validate(state):
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state",
        )

    provider = get_oauth_provider(provider_name)

    user = await provider.authenticate(code, db, )

    access, refresh = TokenService.create_tokens(
        user,
        provider=provider_name,
    )

    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
    }
