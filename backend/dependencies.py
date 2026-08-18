"""
Shared FastAPI dependencies.

This module will grow in later phases to include things like:
- Database session provider (Phase 2)
- Current-user / auth dependency (Phase 2)
- Rate limiting, request context, etc.

Kept intentionally minimal in Phase 1.
"""
from config import Settings, get_settings

__all__ = ["Settings", "get_settings"]