from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1.deps import get_current_user
from src.core.permissions import require_permission
from src.db.postgres import get_db
from src.models.auth import RoleRequest
from src.models.auth import UserResponse, CurrentUser
from src.models.user import User
from src.models.role import UserRole, Permission, ROLE_PERMISSIONS
from src.services.role_service import RoleService

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse,
)
async def assign_role(
        user_id: UUID,
        request: RoleRequest,
        db: AsyncSession = Depends(get_db),
        _: CurrentUser = Depends(
            require_permission(Permission.ASSIGN_ROLES)
        ),
):
    service = RoleService(db)

    return await service.assign_role(
        user_id=user_id,
        role=request.role,
    )


@router.patch(
    "/users/{user_id}/role/reset",
    response_model=UserResponse,
)
async def reset_role(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        _: CurrentUser = Depends(
            require_permission(Permission.ASSIGN_ROLES)
        ),
):
    service = RoleService(db)

    return await service.revoke_role(user_id)


@router.get("/permissions/{permission}")
async def check_permission(
        permission: Permission,
        current_user: CurrentUser = Depends(get_current_user),
):
    return {
        "permission": permission,
        "granted": permission in ROLE_PERMISSIONS[current_user.user.role],
    }
