from uuid import UUID

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import UserRole
from src.services.db_user_service import UserRepository


class RoleService:

    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def assign_role(self, user_id: UUID, role: UserRole):

        user = await self.repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(404, "User not found")

        if role == UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=403,
                detail="SUPER_ADMIN role cannot be managed via API",
            )

        return await self.repository.update_role(user, role)

    async def revoke_role(self, user_id: UUID):

        user = await self.repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(404, "User not found")

        if user.role == UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=403,
                detail="SUPER_ADMIN role cannot be managed via API",
            )

        return await self.repository.update_role(user, UserRole.USER)
