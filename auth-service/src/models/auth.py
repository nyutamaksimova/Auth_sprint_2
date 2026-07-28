from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from src.models.user import User
from src.models.user import UserRole


class UserResponse(BaseModel):
    id: UUID
    username: EmailStr
    role: UserRole

    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    username: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class RoleRequest(BaseModel):
    role: UserRole


@dataclass
class CurrentUser:
    user: User
    payload: dict
