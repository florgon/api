"""
    FastAPI application, entry point.
"""

import uvicorn
from fastapi import FastAPI

from .routers import include_routers
from .middlewares import add_middlewares
from .exception_handlers import add_exception_handlers
from .event_handlers import add_event_handlers
from .database.dependencies import get_db, Session
from .database.bootstrap import dispose_database, bootstrap_database
from .config.logging import hook_fastapi_logger
from .config import get_settings, get_openapi_kwargs, get_logger


def create_application() -> FastAPI:
    """
    Create core FastAPI application with all setup.
    """
    app = FastAPI(
        debug=get_settings().is_development,
        on_startup=[bootstrap_database],
        on_shutdown=[dispose_database],
        **get_openapi_kwargs(),
    )

    app.dependency_overrides[Session] = get_db

    add_event_handlers(app)
    add_exception_handlers(app)
    add_middlewares(app)
    include_routers(app)

    hook_fastapi_logger()

    return app


if __name__ == "__main__":
    get_logger().warn("Booting from raw Uvicorn, please use Gunicorn + Docker pair!")
    uvicorn.run(app="app.app:create_application", factory=True)
