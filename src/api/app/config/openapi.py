"""
    Provides OpenAPI settings (actually, kwargs) for FastAPI application.
"""

from typing import Any
from functools import lru_cache

from pydantic import BaseSettings
from app.__version__ import (
    __version__,
    __url__,
    __title__,
    __terms__,
    __summary__,
    __license_name__,
    __license__,
    __description__,
    __copyright__,
    __author_email__,
    __author__,
)


class OpenAPISettings(BaseSettings):
    """
    Configuration for the OpenAPI (Swagger, ReDoc).
    """

    expose_public: bool = False
    url: str = "/openapi.json"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    prefix: str = ""

    class Config:
        env_prefix = "OPENAPI_"


@lru_cache(maxsize=1)
def get_openapi_kwargs() -> dict[str, Any]:
    settings = OpenAPISettings()
    return {
        "docs_url": settings.docs_url if settings.expose_public else None,
        "redoc_url": settings.redoc_url if settings.expose_public else None,
        "openapi_url": settings.url if settings.expose_public else None,
        "openapi_prefix": settings.prefix,
        "title": __title__,
        "version": __version__,
        "description": __description__,
        "summary": __summary__,
        "terms_of_service": __terms__,
        "contact": {
            "name": __author__,
            "url": __url__,
            "email": __author_email__,
        },
        "license_info": {
            "name": __license_name__,
            "identifier": __license__,
        },
        "openapi_tags": [
            {
                "name": "session",
                "description": "Session workflow methods, cannot be access by default user (direct-auth is allowed only for Florgon services)",
            },
            {
                "name": "user",
                "description": "Methods to get / edit user information or get other user information",
            },
            {
                "name": "utils",
                "description": "Some common utility methods like get status, get features, etc",
            },
            {
                "name": "security",
                "description": "Methods to work with user security information.",
            },
            {
                "name": "tokens",
                "description": "Methods to work with tokens mostly for external services",
            },
            {
                "name": "tickets",
                "description": "Methods to work with ticket system",
            },
        ],
    }
