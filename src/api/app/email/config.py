"""
    Configuration settings.
    ?TODO: Implement different mail provider usage.
"""


from typing import TypeAlias

from fastapi_mail import FastMail, ConnectionConfig
from app.config import get_settings, get_logger

MAIL_PROVIDER: TypeAlias = FastMail
MAIL_CONFIG_PROVIDER: TypeAlias = ConnectionConfig


def _build_connection_config() -> MAIL_CONFIG_PROVIDER | None:
    """
    Setups config for the mail connection from global settings.
    """

    settings = get_settings()
    if not settings.mail_enabled:
        get_logger().warning(
            "[mail] Mail is not enabled with settings! Skipping building connection config..."
        )
        return None

    get_logger().info("[mail] Building connection config...")
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
        SUPPRESS_SEND=0,  # TODO: Check this settings out.
        TEMPLATE_FOLDER=None,
    )


def _build_provider() -> MAIL_PROVIDER | None:
    """
    Builds mail provider (Currently: FastMail package)
    """

    config = _build_connection_config()
    return None if config is None else FastMail(config=config)


provider = _build_provider()
