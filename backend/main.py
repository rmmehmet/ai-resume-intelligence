"""
Application entrypoint.

Creates and configures the FastAPI application instance.
Business logic must never live here - only app wiring.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routers import health_router


def create_app() -> FastAPI:
    """Application factory. Builds and returns a configured FastAPI instance."""
    settings = get_settings()

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

    return app


app = create_app()