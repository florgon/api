"""
    Florgon server API exception handlers.
    (FastAPI exception handlers)
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.services.api.errors import ApiErrorException

from app.tokens.exceptions import (
    TokenExpiredError, 
    TokenInvalidError, 
    TokenInvalidSignatureError, 
    TokenWrongTypeError
)

from . import _handlers


def register_handlers(app: FastAPI) -> None:
    """
        Adds exception handlers for application.
    """

    app.add_exception_handler(ApiErrorException, _handlers._api_error_exception_handler)
    app.add_exception_handler(RequestValidationError, _handlers._validation_exception_handler)

    app.add_exception_handler(TokenExpiredError, _handlers._token_expired_error_handler)
    app.add_exception_handler(TokenWrongTypeError, _handlers._token_wrong_type_error_handler)
    app.add_exception_handler(TokenInvalidError, _handlers._token_invalid_error_handler)
    app.add_exception_handler(TokenInvalidSignatureError, _handlers._token_invalid_signature_error_handler)
    
    app.add_exception_handler(429, _handlers._too_many_requests_handler)

    app.add_exception_handler(404, _handlers._not_found_handler)
    app.add_exception_handler(500, _handlers._internal_server_error_handler)
