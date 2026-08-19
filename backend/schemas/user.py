"""
Pydantic schemas for user data.

These define the API's input/output shapes and are intentionally
separate from the SQLAlchemy model (models/user.py).
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Payload for registering a new user."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str | None = None


class UserLogin(BaseModel):
    """Payload for logging in."""

    email: EmailStr
    password: str


class UserRead(BaseModel):
    """Public-facing representation of a user (never includes the password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime