"""
    Base core class for settings from the environment.
"""
from pydantic import conint, RedisDsn, PostgresDsn, EmailStr, BaseSettings


class Settings(BaseSettings):
    """
    Fetches configuration from the environment variables of the OS.
    Instantiated as some form of the singleton below.

    Information about the configuration is not provided here,
    please see the documentation for more configuration information.
    """

    # Database.
    # TODO: More configuration.
    # ?TODO?: Allow to expose database connection as separate fields.
    database_dsn: PostgresDsn
    database_create_all: bool = True
    database_pool_recycle: int = 3600
    database_pool_timeout: int = 10
    database_max_overflow: int = 0
    database_pool_size: int = 20

    # Prometheus.
    # TODO: More configuration.
    prometheus_metrics_exposed: bool = False

    # Mail.
    mail_enabled: bool = False
    mail_from_name: str | None = None
    mail_from: EmailStr = "noreply@florgon.com"  # type: ignore
    mail_server: str = ""
    mail_password: str = ""
    mail_username: str = ""
    mail_port: int = 587
    mail_starttls: bool = False
    mail_ssl_tls: bool = True
    mail_use_credentials: bool = True
    mail_validate_certs: bool = True
    mail_debug: conint(gt=-1, lt=2) = 0  # type: ignore

    # CORS.
    cors_enabled: bool = True
    cors_allow_credentials: bool = True
    cors_max_age: int = 600
    cors_allow_origins: list[str] = ["*"]
    cors_allow_methods: list[str] = ["GET", "POST", "DELETE", "PUT", "PATCH", "HEAD"]
    cors_allow_headers: list[str] = ["*"]

    # Gatey.
    # TODO: More configuration.
    gatey_is_enabled: bool = False
    gatey_project_id: int | None = None
    gatey_client_secret: str | None = None
    gatey_server_secret: str | None = None
    gatey_capture_requests_info: bool = False

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

    # OpenAPI.
    openapi_enabled: bool = False
    openapi_url: str = "/openapi.json"
    openapi_docs_url: str = "/docs"
    openapi_redoc_url: str = "/redoc"
    openapi_prefix: str = ""
    openapi_title: str = "Florgon API"
    openapi_version: str = "0.0.2"
    openapi_description: str = "Florgon API"

    # FastAPI.
    fastapi_debug: bool = False
    fastapi_root_path: str = ""

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
    # External OAuth.
    auth_ext_oauth_vk_enabled: bool = False
    auth_ext_oauth_vk_client_id: str = ""
    auth_ext_oauth_vk_client_secret: str = ""
    auth_ext_oauth_vk_redirect_uri: str = "/oauth/ext/vk/callback"
    auth_ext_oauth_github_enabled: bool = False
    auth_ext_oauth_github_client_id: str = ""
    auth_ext_oauth_github_client_secret: str = ""
    auth_ext_oauth_github_redirect_uri: str = "/oauth/ext/github/callback"
    auth_ext_oauth_yandex_enabled: bool = False
    auth_ext_oauth_yandex_client_id: str = ""
    auth_ext_oauth_yandex_client_secret: str = ""
    auth_ext_oauth_yandex_redirect_uri: str = "/oauth/ext/yandex/callback"

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

    # Logging.
    # TODO: More configuration.
    logging_logger_name: str = "gunicorn.error"

    # Service.
    # TODO: More configuration.
    service_is_under_maintenance: bool = True
    is_under_debug_environment: bool = True
