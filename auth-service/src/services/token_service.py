from uuid import uuid4

from src.core.security import (
    create_access_token,
    create_refresh_token,
)
from src.models.user import User

from jose import JWTError

from src.core.security import decode_token


class TokenService:

    @staticmethod
    def create_tokens(user: User, provider: str | None = None,):

        payload = {
            "sub": str(user.id),
            "role": user.role.value,
            "jti": str(uuid4()),
            "is_superuser": user.is_superuser,
        }

        if provider:
            payload["provider"] = provider

        access = create_access_token(payload)

        refresh = create_refresh_token(
            {
                "sub": str(user.id),
                "type": "refresh",
            }
        )

        return access, refresh

    @staticmethod
    def validate_refresh(token: str):

        try:
            payload = decode_token(token)

        except Exception:
            return None

        if payload.get("type") != "refresh":
            return None

        return payload
