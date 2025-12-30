from typing import Optional, Annotated
from uuid import UUID
from enum import Enum
from msgspec import Struct, Meta
from litestar.exceptions import HTTPException

from email_validator import validate_email, EmailNotValidError


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserBase(Struct, kw_only=True, omit_defaults=True):
    name: str
    email: str


class UserCreate(Struct, kw_only=True, omit_defaults=True):
    name: str
    email: str
    password: Annotated[str, Meta(min_length=8)]

    def __post_init__(self):
        if not self.name:
            raise HTTPException(detail="Name cannot be empty", status_code=400)
        if not self.email:
            raise HTTPException(detail="Email cannot be empty", status_code=400)
        if not self.password:
            raise HTTPException(detail="Password cannot be empty", status_code=400)

        try:
            validate_email(self.email.strip(), check_deliverability=True)
        except EmailNotValidError:
            raise HTTPException(detail="Invalid email", status_code=400)


class UserRead(UserBase):
    uuid: UUID
    status: bool


class User(Struct, kw_only=True, omit_defaults=True):
    uuid: Optional[UUID] = None
    name: str
    email: str
    password: Optional[str] = None
    fingerprint: Optional[int] = None
    role: Optional[UserRole] = None
    status: Optional[bool] = None


class UserLogin(Struct):
    email: Annotated[str, Meta(min_length=1)]
    password: Annotated[str, Meta(min_length=1)]

    def __post_init__(self):
        if not self.email:
            raise HTTPException(detail="Email cannot be empty", status_code=400)
        if not self.password:
            raise HTTPException(detail="Password cannot be empty", status_code=400)


class Token(Struct):
    access_token: str
    refresh_token: str


class PaginatedUsersResponse(Struct):
    data: list[UserRead]
    total: int
    limit: int
    offset: int
