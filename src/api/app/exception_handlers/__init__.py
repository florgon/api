"""
    Florgon server API exception handlers.
    (FastAPI exception handlers)
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.services.api.errors import ApiErrorException

from . import _handlers


def register_handlers(app: FastAPI) -> None:
    """
        Adds exception handlers for application.
    """

    app.add_exception_handler(ApiErrorException, _handlers._api_error_exception_handler)
    app.add_exception_handler(RequestValidationError, _handlers._validation_exception_handler)
    app.add_exception_handler(404, _handlers._not_found_handler)
    app.add_exception_handler(500, _handlers._internal_server_error_handler)
