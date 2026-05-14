from datetime import datetime

from pydantic import BaseModel, Field


class UserRead(BaseModel):
    user_id: int
    full_name: str
    email: str | None = None
    phone_number: str | None = None
    zalo_id: str | None = None
    role: str
    region: str | None = None
    is_active: bool
    created_at: datetime | None = None


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    phone_number: str | None = Field(default=None, max_length=20)
    zalo_id: str | None = Field(default=None, max_length=100)
    region: str | None = Field(default=None, max_length=100)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
