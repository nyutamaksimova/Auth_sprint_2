from abc import ABC, abstractmethod

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User


class OAuthProvider(ABC):
    """
    Базовый интерфейс OAuth-провайдера.
    """

    @abstractmethod
    async def get_login_url(self, state: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def authenticate(
            self,
            code: str,
            session: AsyncSession,
    ) -> User:
        raise NotImplementedError
