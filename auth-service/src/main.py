from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis
from src.api.v1.auth import router as auth_router
from src.api.v1.roles import router as role_router
from src.api.v1.providers import router as provider_router
from src.core.config import settings
from src.core.init_admin import create_admin_if_not_exists
from src.db.postgres import engine
from src.models.base import Base
from src.core.tracing import setup_tracing
from src.core.middleware import RequestIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True, )

    await create_admin_if_not_exists()

    yield

    await app.state.redis.aclose()


app = FastAPI(
    lifespan=lifespan
)

app.include_router(auth_router)

app.include_router(role_router)

app.include_router(provider_router)

setup_tracing(app)

app.add_middleware(RequestIdMiddleware)
