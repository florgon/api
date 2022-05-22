"""
    API response wrappers.
"""

from typing import Dict, Optional
from fastapi.responses import JSONResponse

from .errors import ApiErrorCode
from .version import API_VERSION


def api_error(api_code: ApiErrorCode, message: str="", data: Optional[Dict] = None) -> JSONResponse:
    """Returns API error response. """

    # Processing arguments.
    if data is None:
        data = {}
    code, status = api_code.value

    return JSONResponse({
        "v": API_VERSION,
        "error": {
            **{"message": message, "code": code, "status": status},
            **data
        }
    }, status_code=status)


def api_success(data: Dict) -> JSONResponse:
    """Returns API success response."""
    return JSONResponse({
        "v": API_VERSION,
        "success": {
            **data
        }
    }, status_code=200)
