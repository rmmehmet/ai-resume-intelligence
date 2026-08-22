"""
SQLAlchemy engine, session factory, and declarative base.

PostgreSQL only - no SQLite fallback. This is the single place the
rest of the app gets a database session from. Routers never touch
this module directly - they use the `get_db` dependency (see
backend/dependencies.py).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import get_settings

settings = get_settings()

if not settings.database_url:
    raise RuntimeError(
        "DATABASE_URL is not set. Set it in your .env file, e.g.:\n"
        "  DATABASE_URL=postgresql://user:password@localhost:5432/resume_ats"
    )

if not settings.database_url.startswith("postgresql"):
    raise RuntimeError(
        "DATABASE_URL must be a PostgreSQL connection string "
        "(postgresql://...). SQLite is no longer supported."
    )

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class all ORM models inherit from."""

    pass