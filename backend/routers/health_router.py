"""
Health check router.

Routers only receive requests and return responses - no business logic here.
"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health_check() -> dict[str, str]:
    """Return a simple status payload confirming the API is running."""
    return {"status": "ok"}