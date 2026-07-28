from fastapi import Depends
from fastapi import HTTPException

from src.api.v1.deps import get_current_user
from src.models.auth import CurrentUser
from src.models.user import User
from src.models.role import UserRole, Permission, ROLE_PERMISSIONS


def require_permission(permission: Permission):
    async def wrapper(
            current_user: CurrentUser = Depends(get_current_user),
    ):

        if current_user.user.is_superuser:
            return current_user

        permissions = ROLE_PERMISSIONS[current_user.user.role]

        if permission not in permissions:
            raise HTTPException(
                status_code=403,
                detail="Permission denied",
            )

        return current_user

    return wrapper
