from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User, UserRole
from uuid import UUID


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.username == email)
        )

        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)

        await self.db.commit()

        await self.db.refresh(user)

        return user

    async def get_by_id(self, user_id: UUID):
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

        return user

    async def update_role(self, user: User, role: UserRole) -> User:
        user.role = role

        await self.db.commit()

        await self.db.refresh(user)

        return user

    async def get_or_create_yandex_user(
            self,
            yandex_user: dict
    ):
        yandex_id = yandex_user["id"]

        user = await self.db.scalar(
            select(User)
            .where(User.yandex_id == yandex_id)
        )

        if user:
            return user

        username = (
                yandex_user.get("default_email")
                or yandex_user.get("login")
        )

        user = User(
            username=username,
            yandex_id=yandex_id,
            password_hash=None,
        )

        self.db.add(user)

        await self.db.commit()
        await self.db.refresh(user)

        return user
