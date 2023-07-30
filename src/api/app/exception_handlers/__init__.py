"""
    FastAPI exception handlers register.
"""

from typing import Callable, Any

from fastapi.exceptions import RequestValidationError
from fastapi import Response, FastAPI
from app.services.tokens.exceptions import (
    TokenWrongTypeError,
    TokenInvalidSignatureError,
    TokenInvalidError,
    TokenExpiredError,
)
from app.services.api import ApiErrorException

from . import handlers

# Binds exception or status code to the handler.
EXCEPTION_MAPPING: dict[Any, Callable[[Any, Any], Response]] = {  # Status codes.
    404: handlers.not_found_handler,
    405: handlers.method_not_allowed,
    429: handlers.too_many_requests_handler,
    500: handlers.internal_server_error_handler,
    # Internal handlers.
    TokenInvalidSignatureError: handlers.token_invalid_signature_error_handler,
    TokenInvalidError: handlers.token_invalid_error_handler,
    TokenWrongTypeError: handlers.token_wrong_type_error_handler,
    TokenExpiredError: handlers.token_expired_error_handler,
    # FastAPI handlers.
    RequestValidationError: handlers.validation_exception_handler,  # type: ignore
    # Service utils.
    ApiErrorException: handlers.api_error_exception_handler,  # type: ignore
}


def add_exception_handlers(app: FastAPI) -> None:
    """
    Adds exception handlers for application.
    """
    for exception, handler in EXCEPTION_MAPPING.items():
        app.add_exception_handler(exception, handler)
