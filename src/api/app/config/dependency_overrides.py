"""
    Provides dict of all dependency overrides for FastAPI.
"""

from typing import Callable, Any

from app.database.dependencies import get_db, Session

DEPENDENCY_OVERRIDES: dict[Callable[..., Any], Callable[..., Any]] = {Session: get_db}
