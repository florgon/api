"""
    Florgon auth API server entry point.
    FastAPI server.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from . import (
    database,
    routers
)


from .services.api.errors import ApiErrorCode, ApiErrorException
from .services.api.response import api_error
from .config import get_settings


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


@app.exception_handler(ApiErrorException)
async def api_error_exception_handler(_, e: ApiErrorException):
    return api_error(e.api_code, e.message, e.data)


# Routers.
for router in [
    routers.oauth_client.router,
    routers.email.router,
    routers.session.router,
    routers.oauth.router,
    routers.user.router,
    routers.utils.router,
    routers.secure.router,
    routers.ext_social_auth.router
]:
     app.include_router(router, prefix=get_settings().proxy_url_prefix)