"""
    Provides base core settings from the environment.
"""

from functools import lru_cache
from enum import Enum

from pydantic import RedisDsn, BaseSettings


class Environment(Enum):
    """
    Switches behaviour of the application according to the environment.

    Development -> Usable for development process where you are not supposed to do significant internal checks.
    Production -> Usable for real deployed version, should not be used inside development environment.
    """

    development = "development"
    production = "production"


class Settings(BaseSettings):
    """
    Fetches configuration from the environment variables of the OS.
    Instantiated as some form of the singleton below.

    Information about the configuration is not provided here,
    please see the documentation for more configuration information.
    TODO: Refactor with split settings.
    """

    environment: Environment = Environment.production

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.development

    # CORS.
    cors_enabled: bool = True
    cors_allow_credentials: bool = True
    cors_max_age: int = 600
    cors_allow_origins: list[str] = ["*"]
    cors_allow_methods: list[str] = ["GET", "POST", "DELETE", "PUT", "PATCH", "HEAD"]
    cors_allow_headers: list[str] = ["*"]

    # Superuser credentials.
    superuser_user_id: int = 1
    superuser_username: str = "admin"
    superuser_password: str = "adminadmin"
    superuser_email: str = "admin@admin.com"

    # Cache backend (Redis).
    # TODO: More configuration.
    cache_dsn: RedisDsn
    cache_encoding: str = "utf-8"

    # Requests limiter.
    # TODO: Allow to handle requests limiter disable better, and do not connect to Redis if not required.
    # TODO: More configuration.
    requests_limiter_enabled: bool = True

    # Caching.
    fastapi_cache_enable: bool = True
    fastapi_cache_use_inmemory_backend: bool = False

    # FastAPI.
    fastapi_debug: bool = False

    # Users.
    # Signup.
    signup_validate_email: bool = True
    signup_username_reject_uppercase: bool = True
    signup_username_reject_nonalpha: bool = True
    signup_open_registration: bool = True
    signup_multiaccounting_dissalowed: bool = False
    # Weird name, means multiaccounting blocked only for signup requests for blocked accounts (sessions).
    # Dissalows creating new account only for users that was blocked and trying to create new account.
    signup_multiaccounting_only_for_non_bypass: bool = False
    # Authentication.
    # Two options below, controls session suspicious check.
    # If true, will block all requests for sessions opened from another IP address (except exception cases).
    auth_reject_wrong_ip_addr: bool = True
    # If true, will block all requests for sessions opened from another user agent (except exception cases).
    auth_reject_wrong_user_agent: bool = True
    # URL of the OAuth screen provider.
    auth_oauth_screen_provider_url: str = "https://florgon.com/oauth/authorize"
    # If true will enable 2FA with email when user verifies email.
    auth_enable_tfa_on_email_verification: bool = True

    # Admin.
    admin_methods_disabled: bool = False

    # Security.
    # JWT Issuer for tokens, should be domain.
    security_tokens_issuer: str = "localhost"
    # Security key for email tokens.
    security_email_tokens_secret_key: str = "RANDOM_SECRET_KEY_TO_BE_SECURE"
    # Time-To-Live for different token types.
    security_email_tokens_ttl: int = 3600
    security_access_tokens_ttl: int = 7776000
    security_refresh_tokens_ttl: int = 7776000
    security_session_tokens_ttl: int = 864000
    security_oauth_code_tokens_ttl: int = 300
    # 2FA TOTP intervals.
    security_tfa_totp_interval_email: int = 3600
    security_tfa_totp_interval_mobile: int = 30

    # Service.
    # TODO: More configuration.
    service_is_under_maintenance: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore
