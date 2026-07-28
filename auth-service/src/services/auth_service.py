import time
from uuid import UUID

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.core.security import hash_password, verify_password
from src.db.redis_db import REFRESH_PREFIX, BLACKLIST_PREFIX
from src.models.auth import RefreshRequest, RegisterRequest, CurrentUser
from src.models.user import User
from src.services.db_user_service import UserRepository
from src.services.token_service import TokenService
import httpx


class AuthService:

    def __init__(self, db: AsyncSession, redis: Redis):
        self.repository = UserRepository(db)
        self.redis = redis

    async def register(self, data: RegisterRequest) -> User:

        exists = await self.repository.get_by_username(data.username)

        if exists:
            raise HTTPException(409, "User already exists")

        user = User(
            username=data.username,
            password_hash=hash_password(data.password)
        )

        return await self.repository.create(user)

    async def login(self, form_data: OAuth2PasswordRequestForm):

        user = await self.repository.get_by_username(form_data.username)

        if not user:
            raise HTTPException(401, "Wrong username or password")

        if not verify_password(form_data.password, user.password_hash):
            raise HTTPException(401, "Wrong username or password")

        access, refresh = TokenService.create_tokens(user)

        await self.redis.set(
            REFRESH_PREFIX + str(user.id),
            refresh,
            ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        )

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
        }

    async def refresh(self, data: RefreshRequest):

        payload = TokenService.validate_refresh(data.refresh_token)

        if payload is None:
            raise HTTPException(401, "Invalid refresh token")

        user_id = payload["sub"]

        stored_token = await self.redis.get(REFRESH_PREFIX + user_id)

        if stored_token is None:
            raise HTTPException(
                401, "Refresh token expired")

        if stored_token != data.refresh_token:
            raise HTTPException(401, "Refresh token revoked")

        user = await self.repository.get_by_id(UUID(user_id))

        if user is None:
            raise HTTPException(404, "User not found")

        access, refresh = TokenService.create_tokens(user)

        await self.redis.delete(REFRESH_PREFIX + user_id)

        await self.redis.set(REFRESH_PREFIX + user_id, refresh,
                             ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
        }

    async def logout(self, current: CurrentUser):

        user = current.user
        payload = current.payload

        key = REFRESH_PREFIX + str(user.id)

        await self.redis.delete(key)

        ttl = payload["exp"] - int(time.time())

        if ttl > 0:
            await self.redis.set(
                BLACKLIST_PREFIX + payload["jti"],
                "1",
                ex=ttl,
            )

        return {"message": "Successfully logged out"}

    async def yandex_callback(self, code: str):
        async with httpx.AsyncClient() as client:

            token_response = await client.post(
                settings.YANDEX_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": settings.YANDEX_CLIENT_ID,
                    "client_secret": settings.YANDEX_CLIENT_SECRET,
                },
            )

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Yandex authentication failed",
                )

            yandex_token = token_response.json()

            yandex_access_token = yandex_token["access_token"]

            user_response = await client.get(
                settings.YANDEX_USERINFO_URL,
                headers={
                    "Authorization": (
                        f"OAuth {yandex_access_token}"
                    )
                },
            )

            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot get Yandex user",
                )

            yandex_user = user_response.json()

        user = self.repository.get_or_create_yandex_user(yandex_user)

        access, refresh = TokenService.create_tokens(
            user,
            provider="yandex",
        )

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
        }
