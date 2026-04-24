from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import TimestampedSchema


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: EmailStr
    password: str


class PermissionRead(TimestampedSchema):
    code: str
    name: str
    description: str | None = None


class RoleRead(TimestampedSchema):
    name: str
    description: str | None = None
    permissions: list[PermissionRead] = Field(default_factory=list)


class UserRead(TimestampedSchema):
    username: str
    email: EmailStr
    full_name: str | None = None
    department: str | None = None
    is_active: bool
    is_superuser: bool
    auth_provider: str
    roles: list[RoleRead] = Field(default_factory=list)
