"""
SQLAlchemy engine, session factory, and declarative base.

This is the single place the rest of the app gets a database session
from. Routers never touch this module directly - they use the
`get_db` dependency (see backend/dependencies.py).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import get_settings

settings = get_settings()

# SQLite needs this connect_arg when used with FastAPI's threaded requests.
# PostgreSQL (production) does not need it and ignores it safely if passed
# conditionally like this.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class all ORM models inherit from."""

    pass