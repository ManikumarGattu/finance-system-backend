from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
import enum


class UserRole(str, enum.Enum):
    viewer  = "viewer"
    analyst = "analyst"
    admin   = "admin"


class UserStatus(str, enum.Enum):
    active   = "active"
    inactive = "inactive"


class UserRegister(BaseModel):
    name:     str      = Field(..., min_length=2, max_length=100)
    email:    EmailStr
    password: str      = Field(..., min_length=6)
    role:     UserRole = UserRole.viewer


class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserStatusUpdate(BaseModel):
    status: UserStatus


class UserUpdate(BaseModel):
    name:   Optional[str]        = None
    role:   Optional[UserRole]   = None
    status: Optional[UserStatus] = None


class UserOut(BaseModel):
    id:         int
    name:       str
    email:      EmailStr
    role:       UserRole
    status:     UserStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListOut(BaseModel):
    id:     int
    name:   str
    email:  EmailStr
    role:   UserRole
    status: UserStatus

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type:   str = "bearer"


class PaginatedUsers(BaseModel):
    total: int
    page:  int
    size:  int
    data:  list[UserListOut]