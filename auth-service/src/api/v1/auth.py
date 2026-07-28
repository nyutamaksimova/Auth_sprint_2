from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1.deps import get_current_user
from src.core.config import settings
from src.db.postgres import get_db
from src.db.redis_db import get_redis
from src.models.auth import CurrentUser
from src.models.auth import RefreshRequest
from src.models.auth import RegisterRequest
from src.models.auth import TokenResponse
from src.models.auth import UserResponse
from src.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201
)
async def register(
        data: RegisterRequest,
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
):
    service = AuthService(db, redis)

    return await service.register(data)


@router.post("/login", response_model=TokenResponse, )
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
):
    service = AuthService(db, redis)

    return await service.login(form_data)


@router.get("/me")
async def me(
        current: CurrentUser = Depends(get_current_user),
):
    user = current.user

    return {
        "id": str(user.id),
        "username": user.username,
        "role": user.role,
    }


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
        data: RefreshRequest,
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
):
    service = AuthService(db, redis)

    return await service.refresh(data)


@router.post("/logout")
async def logout(
        current_user: CurrentUser = Depends(get_current_user),
        redis: Redis = Depends(get_redis),
        db: AsyncSession = Depends(get_db),
):
    service = AuthService(db, redis)

    return await service.logout(current_user)


@router.get("/yandex/login")
async def yandex_login():
    params = {
        "response_type": "code",
        "client_id": settings.YANDEX_CLIENT_ID,
        "redirect_uri": settings.YANDEX_REDIRECT_URI,
    }

    url = f"{settings.YANDEX_AUTHORIZE_URL}?{urlencode(params)}"

    return RedirectResponse(url)


@router.get("/yandex/callback")
async def yandex_callback(
        code: str,
        redis: Redis = Depends(get_redis),
        db: AsyncSession = Depends(get_db),
):
    service = AuthService(db, redis)

    return await service.yandex_callback(code)
