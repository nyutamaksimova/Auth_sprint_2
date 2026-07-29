import secrets

from redis.asyncio import Redis

class OAuthStateService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def create(self) -> str:
        state = secrets.token_urlsafe(32)

        await self.redis.set(
            f"oauth:state:{state}",
            "1",
            ex=300,
        )

        return state

    async def validate(self, state: str) -> bool:

        key = f"oauth:state:{state}"

        exists = await self.redis.get(key)

        if not exists:
            return False

        await self.redis.delete(key)

        return True