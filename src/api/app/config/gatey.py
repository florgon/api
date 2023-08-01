"""
    Gatey configuraion (client).
"""

from functools import lru_cache

from pydantic import BaseSettings
from gatey_sdk.transports import build_transport_instance, VoidTransport
from gatey_sdk.consts import DEFAULT_EVENTS_BUFFER_FLUSH_EVERY
from gatey_sdk.client import Client

from .logging import get_logger


class GateySettings(BaseSettings):
    """
    Configuration for the Gatey client.
    """

    project_id: int | None = None
    client_secret: str | None = None
    server_secret: str | None = None
    send_setup_event: bool = True
    capture_requests_info: bool = False

    @property
    def is_configured(self) -> bool:
        if self.client_secret is not None or self.server_secret is not None:
            return False
        return self.project_id is not None

    class Config:
        env_prefix = "GATEY_"


@lru_cache(maxsize=1)
def get_gatey_settings() -> GateySettings:
    return GateySettings()


@lru_cache(maxsize=1)
def get_gatey_client() -> Client | None:
    settings = GateySettings()
    if not settings.is_configured:
        get_logger().info("[gatey] Skipping, as not configured!")
        return None

    # TODO: Client can do mess so some of the settings is obscured.
    transport = None if settings.is_configured else VoidTransport

    client = Client(
        transport=transport,
        project_id=settings.project_id,
        server_secret=settings.server_secret,
        client_secret=settings.client_secret,
        global_handler_skip_internal_exceptions=True,
        buffer_events_for_bulk_sending=True,
        buffer_events_max_capacity=0,
        buffer_events_flush_every=DEFAULT_EVENTS_BUFFER_FLUSH_EVERY,
        handle_global_exceptions=False,
        include_runtime_info=True,
        include_platform_info=True,
        include_sdk_info=True,
        exceptions_capture_vars=False,
        exceptions_capture_code_context=True,
        access_token=None,  # No need due to internal usage.
        check_api_auth_on_init=False,  # Does auth check below.
    )

    if settings.is_configured and not client.api.do_auth_check():
        get_logger().warning("[gatey] Failed to do auth check!")
        transport = build_transport_instance(
            transport_argument=VoidTransport, api=client.api, auth=client.auth
        )
        assert isinstance(
            transport, VoidTransport
        )  # TODO: Refactor with client SDK fix.
        client.transport = transport

    if settings.send_setup_event:
        client.capture_message(
            level="INFO",
            message="Setup event successfully completed!",
            tags={"is_configured": str(settings.is_configured)},
        )
    return client
