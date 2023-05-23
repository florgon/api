"""
    Mail library configuration settings.
"""

# Settings for configuring mail connection.
from app.config import Settings, get_logger

# Libraries.
from fastapi_mail import ConnectionConfig, FastMail


def _build_connection_config(settings: Settings) -> ConnectionConfig | None:
    """Returns connection configuration for email."""

    if not settings.mail_enabled:
        get_logger().info("Mail is not enabled! Skipping building connection config...")
        return None

    get_logger().info("Building connection config...")
    return ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_FROM=settings.mail_from,
        MAIL_SERVER=settings.mail_server,
        MAIL_FROM_NAME=settings.mail_from_name,
        MAIL_DEBUG=settings.mail_debug,
        MAIL_PORT=settings.mail_port,
        MAIL_STARTTLS=settings.mail_starttls,
        MAIL_SSL_TLS=settings.mail_ssl_tls,
        USE_CREDENTIALS=settings.mail_use_credentials,
        VALIDATE_CERTS=settings.mail_validate_certs,
        SUPPRESS_SEND=0,  # TODO 07.31.22: Check this settings out.
        TEMPLATE_FOLDER=None,
    )


def _build_fastmail(settings: Settings) -> FastMail | None:
    """Returns configured FastMail system."""
    config = _build_connection_config(settings=settings)
    if config is None:
        return None
    return FastMail(config=config)


# Core.
fastmail = _build_fastmail(settings=Settings())
