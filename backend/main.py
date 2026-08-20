"""
Application entrypoint.

Creates and configures the FastAPI application instance.
Business logic must never live here - only app wiring.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from models.ats_score import AtsScore  # noqa: F401 - ensures the model is registered before create_all
from models.job import Job  # noqa: F401 - ensures the model is registered before create_all
from models.match_result import MatchResult  # noqa: F401 - ensures the model is registered before create_all
from models.resume import Resume  # noqa: F401 - ensures the model is registered before create_all
from models.user import User  # noqa: F401 - ensures the model is registered before create_all
from routers import ats_router, auth_router, health_router, job_router, matching_router, resume_router
from services.database.session import Base, engine


def create_app() -> FastAPI:
    """Application factory. Builds and returns a configured FastAPI instance."""
    settings = get_settings()

    # Phase 2: create tables directly for local development. A proper
    # migration tool (Alembic) can replace this once the schema stabilizes.
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router.router)
    app.include_router(auth_router.router)
    app.include_router(resume_router.router)
    app.include_router(ats_router.router)
    app.include_router(job_router.router)
    app.include_router(matching_router.router)

    return app


app = create_app()