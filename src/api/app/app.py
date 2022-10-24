"""
    Florgon API server application entry point.
    Provides FastAPI server.
    Should be run from external process (Manual uvicorn or by default as docker).
"""

from fastapi import FastAPI


from . import database

from .config import get_settings, get_logger, _init_logger

from .event_handlers import add_event_handlers
from .exception_handlers import add_exception_handlers
from .middlewares import add_middlewares
from .routers import include_routers

if __name__ == "__main__":
    # You are not supposed to run this directly.
    # Raise error if tried to run from CLI directly.
    print(
        "ERROR: This application should be run with `Uvicorn` manually, or by Docker (Docker-Compose).\n"
    )
    print(
        "ERROR: Please use methods above, or search FastAPI application inside `/app.py`"
    )
    exit(1)


def _construct_app() -> FastAPI:
    """
    Returns FastAPI application ready to run.
    Creates base FastAPI instance with registering all required stuff on it.
    """

    settings = get_settings()
    app_instance = FastAPI(
        debug=settings.fastapi_debug,
        # Custom settings.
        # By default, modified by setters (below), or empty if not used.
        routes=None,
        middleware=None,
        exception_handlers=None,
        dependencies=None,
        responses=None,
        callbacks=None,
        # Event handlers.
        on_shutdown=None,
        on_startup=None,
        # Open API.
        title=settings.openapi_title,
        version=settings.openapi_version,
        description=settings.openapi_description,
        openapi_prefix=settings.openapi_prefix,
        openapi_url=settings.openapi_url if settings.openapi_enabled else None,
        docs_url=settings.openapi_docs_url if settings.openapi_enabled else None,
        redoc_url=settings.openapi_redoc_url if settings.openapi_enabled else None,
        # Other.
        root_path=settings.fastapi_root_path,
        root_path_in_servers=True,
    )

    # Initializing database connection and all ORM stuff.
    if settings.database_create_all:
        database.core.create_all()

    # Register all internal stuff as routers/handlers/middlewares etc.
    add_event_handlers(app_instance)
    add_exception_handlers(app_instance)
    add_middlewares(app_instance)
    include_routers(app_instance)

    # Logging.
    _init_logger()
    get_logger().info("Successfully initalized FastAPI application with logger!")
    
    return app_instance


# Root application for uvicorn runner or whatever else.
# (Docker compose is running with app.app:app, means that this application instance
# will be served by uvicorn, and will be constructed at import).
app = _construct_app()
