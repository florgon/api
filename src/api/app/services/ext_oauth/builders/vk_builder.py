"""
    VK OAuth provider builder (service).
"""

from app.services.ext_oauth.providers.vk_provider import VkOauthService
from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.config import get_settings


def build_vk_oauth_service(vk_oauth_display: str | None = None) -> VkOauthService:
    """
    Returns VK OAuth provider (service).
    """
    settings = get_settings()

    if not settings.auth_ext_oauth_vk_enabled:
        raise ApiErrorException(
            ApiErrorCode.API_FORBIDDEN,
            "VK OAuth currently disabled by server administrators.",
        )

    return VkOauthService(
        client_id=settings.auth_ext_oauth_vk_client_id,
        client_secret=settings.auth_ext_oauth_vk_client_secret,
        client_redirect_uri=settings.auth_ext_oauth_vk_redirect_uri,
        display=vk_oauth_display,
    )
