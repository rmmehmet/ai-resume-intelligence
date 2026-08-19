"""
Shared FastAPI dependencies.

Routers depend on these functions instead of reaching into services
or the database layer directly, keeping that wiring in one place.
"""
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import Settings, get_settings
from models.user import User
from services.auth.security import decode_access_token
from services.auth.service import get_user_by_email
from services.database.session import SessionLocal

__all__ = ["Settings", "get_settings", "get_db", "get_current_user"]

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for the duration of a single request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(_oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the current authenticated user from the request's bearer token."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_error

    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_error

    return user