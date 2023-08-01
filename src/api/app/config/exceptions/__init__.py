"""
    FastAPI exception handlers.
"""

from typing import Union, Type, Coroutine, Callable, Any

from fastapi.exceptions import RequestValidationError
from fastapi import Response, Request
from app.services.tokens.exceptions import (
    TokenWrongTypeError,
    TokenInvalidSignatureError,
    TokenInvalidError,
    TokenExpiredError,
)
from app.services.api import ApiErrorException

from . import handlers

EXCEPTION_HANDLERS: dict[
    Union[int, Type[Exception]],
    Callable[[Request, Any], Coroutine[Any, Any, Response]],
] = {
    404: handlers.not_found_handler,
    405: handlers.method_not_allowed,
    429: handlers.too_many_requests_handler,
    500: handlers.internal_server_error_handler,
    TokenInvalidSignatureError: handlers.token_invalid_signature_error_handler,
    TokenInvalidError: handlers.token_invalid_error_handler,
    TokenWrongTypeError: handlers.token_wrong_type_error_handler,
    TokenExpiredError: handlers.token_expired_error_handler,
    RequestValidationError: handlers.validation_exception_handler,
    ApiErrorException: handlers.api_error_exception_handler,
}
