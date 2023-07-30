"""
    Service for API responses.
    
    Used for formatting response payload into custom (for Florgon APIs) response (FastAPI response object).
    
    Used both for response and errors (as response or exception with exception handler).
"""

from .response import api_success, api_error
from .errors import ApiErrorException, ApiErrorCode
from . import response, errors

__all__ = [
    "response",
    "errors",
    "api_error",
    "api_success",
    "ApiErrorCode",
    "ApiErrorException",
]
