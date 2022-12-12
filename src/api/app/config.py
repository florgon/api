"""
    Configuration fields.
    Pydantic BaseSettings interface with reading from OS environment variables.
    Other instances to work with.
    Variables should passed by Docker.
"""

# Logs.
import logging

# Pydantic abstract class with data types.
from pydantic import BaseSettings, EmailStr, PostgresDsn, RedisDsn, conint

# Libs.
import gatey_sdk


class Settings(BaseSettings):
    """
    All settings storage.
    """

    # Database.

    # Database connection string (DSN)
    # TODO 07.31.22: Allow to expose database connection as separate fields.
    database_dsn: PostgresDsn
    # If true, will create all metadata (Tables) at start of the server.
    database_create_all: bool = True
    # Pool recycle for ORM (Database).
    database_pool_recycle: int = 3600
    # Timeout for database pool.
    database_pool_timeout: int = 10
    # Max overflow for database pool.
    database_max_overflow: int = 0
    # Pool size for database pool.
    database_pool_size: int = 20

    # Prometheus (Grafana)
    prometheus_metrics_exposed: bool = False

    # Mail.

    # If false, email will be disabled and not even sent.
    mail_enabled: bool = False
    # Optional name for email (Like: "Florgon <noreply@florgon.space>")
    mail_from_name: str | None = None
    # Mail from email.
    mail_from: EmailStr = "noreply@florgon.space"
    # Mail server authentication.
    mail_server: str = ""
    mail_password: str = ""
    mail_username: str = ""
    # Mail server configuration.
    mail_port: int = 587
    mail_starttls: bool = False
    mail_ssl_tls: bool = True
    mail_use_credentials: bool = True
    mail_validate_certs: bool = True
    # Utils.
    mail_debug: conint(gt=-1, lt=2) = 0

    # CORS.

    # If true, will add CORS middleware.
    cors_enabled: bool = True
    # Will allow to send Authorization header.
    cors_allow_credentials: bool = True
    # Max age for CORS.
    cors_max_age: int = 600
    # Allowed CORS stuff.
    cors_allow_origins: list[str] = ["*"]
    cors_allow_methods: list[str] = ["GET", "HEAD"]
    cors_allow_headers: list[str] = ["*"]

    # Gatey.
    gatey_is_enabled: bool = (
        True  # By default should not fail as will use void transport.
    )
    gatey_project_id: int | None = None
    gatey_client_secret: str | None = None  # Not preferable.
    gatey_server_secret: str | None = None

    # Cache.

    # Redis connection string.
    cache_dsn: RedisDsn
    # Encoding for Redis.
    cache_encoding: str = "utf-8"

    # Requests limiter.

    # TODO 07.31.22: Allow to handle requests limiter disable better, and do not connect to Redis if not required.
    requests_limiter_enabled: bool = True

    # OpenAPI.

    # If false, will disable OpenAPI.
    openapi_enabled: bool = False
    openapi_url: str = "/openapi.json"
    openapi_docs_url: str = "/docs"
    openapi_redoc_url: str = "/redoc"
    openapi_prefix: str = ""
    openapi_title: str = "Florgon API"
    openapi_version: str = "0.0.0"
    openapi_description: str = "Florgon API"

    # FastAPI.

    # Should be false in production.
    fastapi_debug: bool = False
    fastapi_root_path: str = ""

    # Users.

    # If true, will validate email field when sign-up
    signup_validate_email: bool = True
    # If true, will reject all usernames with uppercase symbols.
    signup_username_reject_uppercase: bool = True
    # If true will reject all usernames with non alphabetic characters.
    signup_username_reject_nonalpha: bool = True
    # If false will reject all signup requests.
    signup_open_registration: bool = True

    # Authentication.
    # Two options below, controls session suspicious check.
    # If true, will block all requests for sessions opened from another IP address (except exception cases).
    auth_reject_wrong_ip_addr: bool = True
    # If true, will block all requests for sessions opened from another user agent (except exception cases).
    auth_reject_wrong_user_agent: bool = True
    # URL of the OAuth screen provider.
    auth_oauth_screen_provider_url: str = "https://florgon.space/oauth/authorize"
    # If true will enable 2FA with email when user verifies email.
    auth_enable_tfa_on_email_verification: bool = True
    # External VK OAuth service configuration.
    auth_ext_oauth_vk_enabled: bool = False
    auth_ext_oauth_vk_client_id: str = ""
    auth_ext_oauth_vk_client_secret: str = ""
    auth_ext_oauth_vk_redirect_uri: str = "/oauth/ext/vk/callback"
    # External GitHub OAuth service configuration
    auth_ext_oauth_github_enabled: bool = False
    auth_ext_oauth_github_client_id: str = ""
    auth_ext_oauth_github_client_secret: str = ""
    auth_ext_oauth_github_redirect_uri: str = "/oauth/ext/github/callback"
    # External Yandex OAuth service configuration
    auth_ext_oauth_yandex_enabled: bool = False
    auth_ext_oauth_yandex_client_id: str = ""
    auth_ext_oauth_yandex_client_secret: str = ""
    auth_ext_oauth_yandex_redirect_uri: str = "/oauth/ext/yandex/callback"

    # Proxy (Server content with prefix or domain (Proxy server)).

    # Will be added to all methods.
    proxy_url_prefix: str = ""
    # Used for email sending with backling to API (WIP, TODO, Will be removed).
    proxy_url_domain: str = "http://localhost"

    # Admin.

    # If true, will disallow access to admin methods even if admin.
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

    # Logging.
    logging_logger_name: str = "gunicorn.error"


def _init_gatey_client(settings: Settings) -> gatey_sdk.Client | None:
    """
    Initializes Gatey client and returns it.
    """

    if not settings.gatey_is_enabled:
        return None

    gatey_is_configured = (
        settings.gatey_client_secret is not None
        or settings.gatey_server_secret is not None
    ) and settings.gatey_project_id is not None
    gatey_transport = None if gatey_is_configured else gatey_sdk.VoidTransport
    gatey_client = gatey_sdk.Client(
        transport=gatey_transport,
        project_id=settings.gatey_project_id,
        client_secret=settings.gatey_client_secret,
        server_secret=settings.gatey_server_secret,
        check_api_auth_on_init=False,
        handle_global_exceptions=False,
        global_handler_skip_internal_exceptions=False,
        buffer_events_for_bulk_sending=True,
        buffer_events_max_capacity=1,
        exceptions_capture_vars=False,
        exceptions_capture_code_context=True,
        buffer_events_flush_every=10.0,
        include_runtime_info=True,
        include_platform_info=True,
        include_sdk_info=True,
    )
    if gatey_is_configured and not gatey_client.api.do_auth_check():
        get_logger().warning("Gatey SDK failed to check Auth!")
        return None

    gatey_client.capture_message(
        level="INFO",
        message="[Florgon API] Server successfully initialized Gatey client (gatey-sdk-py)",
    )
    return gatey_client


def get_logger() -> logging.Logger:
    """
    Returns Singleton logger object for logging.
    """
    return _logger


def get_settings() -> Settings:
    """
    Returns Singleton settings object with all configuration settings.
    """
    return _settings


def get_gatey_client() -> gatey_sdk.Client:
    """
    Returns Singleton Gatey client object.
    """
    return _gatey


# Static objects.
_settings = Settings()
_gatey = _init_gatey_client(_settings)
_logger = logging.getLogger(
    _settings.logging_logger_name if _settings.logging_logger_name else __name__
)
