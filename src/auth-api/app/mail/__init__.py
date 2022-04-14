# Libraries.
from fastapi_mail import (
    FastMail, ConnectionConfig, MessageSchema
)

# Settings for configuring mail connection.
from app.config import Settings

# Config for mail.
settings = Settings()
config = ConnectionConfig(
    MAIL_USERNAME = settings.mail_host_username,
    MAIL_PASSWORD = settings.mail_host_password,
    MAIL_FROM = settings.mail_host_username,
    MAIL_SERVER = settings.mail_host_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_PORT = 587,
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)


async def send(email: str, subject: str, body: str):
    """ Sends message to single recepient email. """
    fastmail = FastMail(config)
    await fastmail.send_message(MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype="plain"
    ))