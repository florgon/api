from .settings import Settings
from .__version__ import (
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

OPENAPI_TAGS = [
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
]


def get_fastapi_openapi_kwargs(settings: Settings) -> dict:
    return {
        "docs_url": settings.openapi_docs_url if settings.openapi_enabled else None,
        "redoc_url": settings.openapi_redoc_url if settings.openapi_enabled else None,
        "openapi_url": settings.openapi_url if settings.openapi_enabled else None,
        "openapi_prefix": settings.openapi_prefix,
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
        "openapi_tags": OPENAPI_TAGS,
    }
