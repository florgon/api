"""
    Mail (email) environment settings.
"""

from functools import lru_cache

from pydantic import EmailStr, BaseSettings
from fastapi_mail import FastMail, ConnectionConfig
from aiosmtplib.smtp import (
    SMTP_TLS_PORT,
    SMTP_STARTTLS_PORT,
    SMTP_PORT,
    DEFAULT_TIMEOUT,
)

from .settings import get_settings, Environment


class MailSettings(BaseSettings):
    """
    Configuration for the mail provider.
    """

    # Some alternative to disabling mail,
    # will *supress* (not send) any mail.
    supress_send: bool = True

    server: str = ""
    password: str = ""
    username: str = ""

    from_name: str | None = None
    from_mail: EmailStr | None = None

    port: int | None = None
    starttls: bool = False
    ssl_tls: bool = True
    use_credentials: bool = True
    validate_certs: bool = True
    timeout: int = DEFAULT_TIMEOUT

    @property
    def real_from_mail(self):
        return self.from_mail or "boilerplate@mail.com"

    @property
    def real_supress_send(self):
        return (
            self.supress_send
            if get_settings().environment != Environment.development
            else False
        )

    @property
    def real_port(self):
        if self.starttls and self.ssl_tls:
            raise ValueError("Please define STARTTLS or SSL_TLS, not both!")
        if self.port is not None:
            return self.port
        if self.starttls:
            return SMTP_STARTTLS_PORT
        return SMTP_TLS_PORT if self.ssl_tls else SMTP_PORT

    class Config:
        env_prefix = "MAIL_"


@lru_cache(maxsize=1)
def get_mail_settings() -> MailSettings:
    return MailSettings()


@lru_cache(maxsize=1)
def get_mail() -> FastMail:
    settings = get_mail_settings()
    return FastMail(
        config=ConnectionConfig(
            MAIL_USERNAME=settings.username,
            MAIL_PASSWORD=settings.password,
            MAIL_FROM=settings.real_from_mail,
            MAIL_SERVER=settings.server,
            MAIL_FROM_NAME=settings.from_name,
            MAIL_PORT=settings.real_port,
            MAIL_STARTTLS=settings.starttls,
            MAIL_SSL_TLS=settings.ssl_tls,
            USE_CREDENTIALS=settings.use_credentials,
            VALIDATE_CERTS=settings.validate_certs,
            SUPPRESS_SEND=int(settings.real_supress_send),
            TIMEOUT=settings.timeout,
            TEMPLATE_FOLDER=None,  # TODO: Add support for templates.
            MAIL_DEBUG=0,  # Not used by lib.
        )
    )
