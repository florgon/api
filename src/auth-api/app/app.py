"""
    Florgon auth API server entry point.
    FastAPI server.
"""

# Libraries.
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

# Local libraries.
from . import (
    database,
    routers
)

# Services.
from .services.api.errors import ApiErrorCode
from .services.api.response import api_error

# Other.
from .config import Settings


# Creating application.
database.core.create_all()
app = FastAPI(docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exception):
    """ Custom validation exception handler. """
    return api_error(ApiErrorCode.API_INVALID_REQUEST, "Invalid request!", {
        "exc": str(exception)
    })

@app.exception_handler(404)
async def not_found_handler(_, __):
    return api_error(ApiErrorCode.API_METHOD_NOT_FOUND, "Method not found!")

@app.exception_handler(500)
async def internal_server_error_handler(_, __):
    return api_error(ApiErrorCode.API_INTERNAL_SERVER_ERROR, "Internal server error!")


# Routers.
proxy_url_prefix = Settings().proxy_url_prefix
app.include_router(routers.oauth_client.router, prefix=proxy_url_prefix)
app.include_router(routers.email.router, prefix=proxy_url_prefix)
app.include_router(routers.session.router, prefix=proxy_url_prefix)
app.include_router(routers.oauth.router, prefix=proxy_url_prefix)
app.include_router(routers.user.router, prefix=proxy_url_prefix)