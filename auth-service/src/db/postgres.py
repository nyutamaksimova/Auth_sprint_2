from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from src.core.config import settings

DATABASE_URL = (f"postgresql+asyncpg://"
                f"{settings.POSTGRES_USER}:"
                f"{settings.POSTGRES_PASSWORD}@"
                f"{settings.DB_HOST}:"
                f"{settings.DB_PORT}/"
                f"{settings.POSTGRES_DB}"
                )

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.POSTGRES_ECHO,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
