"""
    Mail library configuration settings.
"""

# Libraries.
from fastapi_mail import ConnectionConfig, FastMail

# Settings for configuring mail connection.
from app.config import Settings


def _build_connection_config(settings: Settings) -> ConnectionConfig | None:
    """Returns connection configuration for email."""

    if not settings.mail_enabled:
        return None

    return ConnectionConfig(
        MAIL_USERNAME=settings.mail_host_username,
        MAIL_PASSWORD=settings.mail_host_password,
        MAIL_FROM=settings.mail_host_username,
        MAIL_SERVER=settings.mail_host_server,
        MAIL_FROM_NAME=settings.mail_from_name,
        MAIL_DEBUG=1,
        MAIL_PORT=587,
        MAIL_TLS=True,
        MAIL_SSL=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )


def _build_fastmail(settings: Settings) -> None:
    """Returns configured FastMail system."""
    config = _build_connection_config(settings=settings)
    if config is None:
        return None
    return FastMail(config=config)


# Core.
fastmail = _build_fastmail(settings=Settings())