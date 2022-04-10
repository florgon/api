"""
    Florgon auth API server entry point.
    FastAPI server.
"""

# Libraries.
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

# Local libraries.
import database
import routers

# Services.
from services.api.errors import ApiErrorCode
from services.api.response import api_error

# Other.
from config import Settings


# Creating application.
database.core.create_all()
app = FastAPI(docs_url=None, redoc_url=None)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exception):
    """ Custom validation exception handler. """
    return api_error(ApiErrorCode.API_INVALID_REQUEST, "Invalid request!", {
        "exc": str(exception)
    })


# Routers.
proxy_url_prefix = Settings().proxy_url_prefix
app.include_router(routers.root.router, prefix=proxy_url_prefix)
app.include_router(routers.auth.router, prefix=proxy_url_prefix)