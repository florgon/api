"""
    API response wrappers.
"""

from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.__version__ import __version__

from .errors import ApiErrorCode


def api_error(
    api_code: ApiErrorCode,
    message: str = "",
    data: dict | None = None,
    headers: dict | None = None,
) -> JSONResponse:
    """Returns API error response."""

    data = data or dict()
    headers = headers or dict()
    code, status = api_code.value

    return JSONResponse(
        {
            "v": __version__,
            "error": {"message": message, "code": code, "status": status} | data,
        },
        status_code=status,
        headers=headers,
    )


def api_success(data: dict | BaseModel) -> JSONResponse:
    """Returns API success response."""
    if isinstance(data, BaseModel):
        data = data.dict()
    return JSONResponse({"v": __version__, "success": data}, status_code=200)
