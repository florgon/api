"""
    Config environment variables reader.
"""

from pydantic import BaseSettings, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Base settings."""

    database_url: PostgresDsn
    database_pool_size: int = 20  # Pool size (or 0 for no pool limit).
    cache_url: RedisDsn

    upload_server_domain: str = "cdnus0.florgon.space"

    oauth_screen_provider_url: str = "oauth.florgon.space"

    jwt_issuer: str

    access_token_jwt_ttl: int
    session_token_jwt_ttl: int
    oauth_code_jwt_ttl: int

    cft_secret: str
    cft_salt: str
    cft_max_age: int

    proxy_url_prefix: str
    proxy_url_host: str

    mail_enabled: bool
    mail_from_name: str
    mail_host_server: str
    mail_host_password: str
    mail_host_username: str

    tfa_otp_email_inteval: int = 60 * 5
    tfa_otp_mobile_inteval: int = 30
    
    # Not documented yet.
    user_enable_email_tfa_by_default: bool = False
    users_open_registration: bool = True
    cors_enabled: bool = True
    fastapi_debug: bool = False
    fastapi_title: str = "Florgon API"
    fastapi_description: str = "Florgon main API (Built with FastAPI)"
    fastapi_documentation_enabled: bool = False


_settings = Settings()


def get_settings():
    return _settings
