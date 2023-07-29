"""
    Configuration fields.
    Interface with reading from OS environment variables.
    Other instances to work with.
    Variables should passed by Docker.
"""

import logging

import gatey_sdk

from .settings import Settings


def _init_gatey_client(settings: Settings) -> gatey_sdk.Client | None:
    """
    Constructor for the Gatey client with configuration.
    ?TODO?: Maybe move inside module instead?
    """

    if not settings.gatey_is_enabled:
        return None

    # TODO: More configuration.
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
        get_logger().warning("[gatey] Gatey SDK failed to check auth, skipping setup!")
        return None

    gatey_client.capture_message(
        level="INFO",
        message="[Florgon API] Server successfully initialized Gatey client (gatey-sdk-py)",
    )
    return gatey_client


def get_logger() -> logging.Logger:
    """Returns Singleton logger object for logging."""
    return _logger


def get_settings() -> Settings:
    """Returns Singleton settings object with all configuration settings."""
    return _settings


def get_gatey_client() -> gatey_sdk.Client | None:
    """Returns Singleton Gatey client object."""
    return _gatey


# Static objects.
# (Order should be same like now!)
_settings = Settings()  # type: ignore[call-arg]
_logger = logging.getLogger(_settings.logging_logger_name or __name__)
_gatey = _init_gatey_client(_settings)
