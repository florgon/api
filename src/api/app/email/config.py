"""
    Mail library configuration settings.
"""


# Libraries.
from fastapi_mail import ConnectionConfig

# Settings for configuring mail connection.
from app.config import Settings

# Config for mail.
settings = Settings()
config = None
if settings.mail_enabled:
    config = ConnectionConfig(
        MAIL_USERNAME=settings.mail_host_username,
        MAIL_PASSWORD=settings.mail_host_password,
        MAIL_FROM=settings.mail_host_username,
        MAIL_SERVER=settings.mail_host_server,
        MAIL_FROM_NAME=settings.mail_from_name,
        MAIL_PORT=587,
        MAIL_TLS=True,
        MAIL_SSL=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
