import http
from typing import Optional

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from src.core.config import settings


class TokenPayload(BaseModel):
    sub: str
    role: str
    jti: str
    is_superuser: bool
    exp: int


def decode_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if not payload.get("sub"):
            return None

        return TokenPayload(**payload)

    except JWTError as e:
        print("Invalid JWT: %s", e)
        return None


class JWTBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:

        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid authorization code.')
        if not credentials.scheme == 'Bearer':
            raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED, detail='Only Bearer token might be accepted')
        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid or expired token.')

        request.state.user = decoded_token
        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> Optional[TokenPayload]:
        return decode_token(jwt_token)


security_jwt = JWTBearer()


class RoleChecker:
    def __init__(self, roles: list[str]):
        self.roles = roles

    def __call__(self, user: TokenPayload = Depends(security_jwt)):
        if not user.role in self.roles:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )

        return user
