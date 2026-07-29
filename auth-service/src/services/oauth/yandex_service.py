from urllib.parse import urlencode

import httpx
from fastapi import HTTPException
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.models.user import User
from src.services.db_user_service import UserRepository
from src.services.oauth.base import OAuthProvider
from src.services.oauth.state import OAuthStateService


class YandexOAuthProvider(OAuthProvider):
    PROVIDER_NAME = 'yandex'

    AUTHORIZE_URL = "https://oauth.yandex.ru/authorize"
    TOKEN_URL = "https://oauth.yandex.ru/token"
    USERINFO_URL = "https://login.yandex.ru/info"

    async def get_login_url(self, state: str) -> str:

        params = {
            "response_type": "code",
            "client_id": settings.YANDEX_CLIENT_ID,
            "redirect_uri": settings.YANDEX_REDIRECT_URI,
            "state": state
        }

        return f"{self.AUTHORIZE_URL}?{urlencode(params)}"

    async def authenticate(
            self,
            code: str,
            db: AsyncSession,
    ) -> User:

        repository = UserRepository(db)
        async with httpx.AsyncClient(timeout=10) as client:
            access_token = await self._get_access_token(client, code)

            profile = await self._get_profile(client, access_token)

        user = await repository.get_or_create_yandex_user(profile)

        return user

    async def _get_access_token(
            self,
            client: AsyncClient,
            code: str,
    ) -> str:
        try:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": settings.YANDEX_CLIENT_ID,
                    "client_secret": settings.YANDEX_CLIENT_SECRET,
                },
            )
            response.raise_for_status()
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Yandex OAuth request timed out",
            )

        except httpx.HTTPStatusError:

            raise HTTPException(
                status_code=400,
                detail="Failed to authorize with Yandex",
            )

        except httpx.HTTPError:
            raise HTTPException(
                status_code=502,
                detail="Unable to connect to Yandex OAuth service",
            )

        return response.json()["access_token"]

    async def _get_profile(
            self,
            client: AsyncClient,
            access_token: str,
    ) -> dict:
        try:
            response = await client.get(
                self.USERINFO_URL,
                headers={
                    "Authorization": f"OAuth {access_token}",
                },
            )

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Yandex user info request timed out",
            )

        except httpx.HTTPStatusError:
            raise HTTPException(
                status_code=400,
                detail="Failed to retrieve Yandex profile",
            )

        except httpx.HTTPError:
            raise HTTPException(
                status_code=502,
                detail="Unable to connect to Yandex user service",
            )

        return response.json()
