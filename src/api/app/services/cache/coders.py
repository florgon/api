"""
    Coders for response value (data) for caching.
"""

import json
from typing import Dict, Any

from starlette.responses import JSONResponse

# Base coder.
from fastapi_cache.coder import object_hook, JsonEncoder, Coder


class JSONResponseCoder(Coder):
    """
    Response coder that converts response to string for caching in storage as JSON.
    """

    @classmethod
    def encode(cls, value: Any):
        """
        Converts response to string for caching in storage.
        """
        if isinstance(value, JSONResponse):
            # We are caching special response, that should encoded differently.
            value = {
                "headers": _raw_headers_back_to_headers(
                    headers_as_bytes=value.raw_headers, skip_internal_calculated=True
                ),
                # Content is only can be accessed by decoding body.
                "content": json.loads(value.body.decode(value.charset)),
                "status_code": value.status_code,
                # Internal flag for cached value.
                "_cls_type": "JSONResponse",
            }
        return json.dumps(
            value,
            cls=JsonEncoder,
        )

    @classmethod
    def decode(cls, value: Any) -> JSONResponse | Dict[Any, Any]:
        """
        Converts cached value back to response or dict.
        """
        parsed_values = json.loads(value, object_hook=object_hook)
        if parsed_values.get("_cls_type") == "JSONResponse":
            # We are cached special response, that should re-build back.
            return JSONResponse(
                content=parsed_values.get("content", dict()),
                headers=parsed_values.get("headers", dict()),
                status_code=parsed_values.get("status_code", 200),
                background=None,
            )

        # Just plain parsed dict.
        return parsed_values


def _raw_headers_back_to_headers(
    headers_as_bytes: list[tuple[bytes, bytes]], skip_internal_calculated: bool = True
) -> Dict[str, str]:
    """
    Converts raw headers back to default headers with removing internal calculated.
    """
    parsed_headers = dict()

    for raw_header in headers_as_bytes:
        # Decode raw headers to dictionary.
        h_name, h_value = raw_header
        parsed_headers[h_name.decode()] = h_value.decode("latin-1")

    if skip_internal_calculated:
        # Will remove headers that fails rendering as will change checksum (length / type)
        parsed_headers.pop("content-length", None)
        parsed_headers.pop("content-type", None)

    return parsed_headers
