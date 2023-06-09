"""
    GitHub OAuth provider builder (service).
"""

from app.services.ext_oauth.providers.github_provider import GithubOauthService
from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.config import get_settings


def build_github_oauth_service() -> GithubOauthService:
    """
    Returns GitHub OAuth provider (service).
    """
    settings = get_settings()

    if not settings.auth_ext_oauth_github_enabled:
        raise ApiErrorException(
            ApiErrorCode.API_FORBIDDEN,
            "GitHub OAuth currently disabled by server administrators.",
        )

    return GithubOauthService(
        client_id=settings.auth_ext_oauth_github_client_id,
        client_secret=settings.auth_ext_oauth_github_client_secret,
        client_redirect_uri=settings.auth_ext_oauth_github_redirect_uri,
    )
