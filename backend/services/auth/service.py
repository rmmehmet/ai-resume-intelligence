"""
Auth business logic.

This is the only place that knows how registration/login actually
work. Routers call these functions; they never touch the database
or security primitives directly.
"""
from sqlalchemy.orm import Session

from models.user import User
from schemas.user import UserCreate
from services.auth.security import create_access_token, hash_password, verify_password


class EmailAlreadyRegisteredError(Exception):
    """Raised when attempting to register an email that already exists."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials are incorrect."""


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def register_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user account. Raises EmailAlreadyRegisteredError on duplicate email."""
    if get_user_by_email(db, user_in.email) is not None:
        raise EmailAlreadyRegisteredError(f"Email already registered: {user_in.email}")

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Verify credentials and return the user. Raises InvalidCredentialsError if invalid."""
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError("Incorrect email or password")
    if not user.is_active:
        raise InvalidCredentialsError("User account is inactive")
    return user


def create_token_for_user(user: User) -> str:
    """Issue a JWT access token for an authenticated user."""
    return create_access_token(subject=user.email)