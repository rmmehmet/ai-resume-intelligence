"""
Pydantic schemas for authentication tokens.
"""
from pydantic import BaseModel


class Token(BaseModel):
    """Response returned after a successful login."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload shape."""

    sub: str | None = None