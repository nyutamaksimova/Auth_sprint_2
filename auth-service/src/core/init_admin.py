from sqlalchemy import select

from src.core.config import settings
from src.core.security import hash_password
from src.db.postgres import AsyncSessionLocal
from src.models.user import User, UserRole


async def create_admin_if_not_exists():
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        return

    async with AsyncSessionLocal() as session:
        exists = await session.scalar(
            select(User).where(
                User.username == settings.ADMIN_EMAIL
            )
        )

        if exists:
            return

        admin = User(
            username=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role=UserRole.SUPER_ADMIN,
            is_superuser=True,
        )

        session.add(admin)
        await session.commit()
