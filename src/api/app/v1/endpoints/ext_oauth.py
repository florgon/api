"""
    External OAuth router.
    Provides API methods (routes) for working with social accounts OAuth.
"""

from app.core.config import get_settings
from app.core.services.api.errors import ApiErrorCode
from app.core.services.api.response import api_error
from app.core.services.ext_oauth.github_provider import GithubOauthService
from app.core.services.ext_oauth.vk_provider import VkOauthService
from app.core.services.ext_oauth.yandex_provider import YandexOauthService
from fastapi import APIRouter
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter()


@router.get("/extOauthVk.requestSignin")
async def method_ext_oauth_vk_request_signin(display: str = "page") -> JSONResponse:
    """OAuth with external OAuth VK provider."""

    settings = get_settings()

    if not settings.auth_ext_oauth_vk_enabled:
        return api_error(
            ApiErrorCode.API_FORBIDDEN,
            "VK OAuth currently disabled by server administrators.",
        )

    vk_oauth_display = display
    vk_oauth_service = VkOauthService(
        client_id=settings.auth_ext_oauth_vk_client_id,
        client_secret=settings.auth_ext_oauth_vk_client_secret,
        client_redirect_uri=settings.auth_ext_oauth_vk_redirect_uri,
        display=vk_oauth_display,
    )

    authorize_url = vk_oauth_service.get_authorize_url()
    return RedirectResponse(url=authorize_url)


@router.get("/extOauthGithub.requestSignin")
async def method_ext_oauth_github_request_signin() -> JSONResponse:
    """OAuth with external OAuth GitHub provider."""

    settings = get_settings()

    if not settings.auth_ext_oauth_github_enabled:
        return api_error(
            ApiErrorCode.API_FORBIDDEN,
            "GitHub OAuth currently disabled by server administrators.",
        )

    github_oauth_service = GithubOauthService(
        client_id=settings.auth_ext_oauth_github_client_id,
        client_secret=settings.auth_ext_oauth_github_client_secret,
        client_redirect_uri=settings.auth_ext_oauth_github_redirect_uri,
    )

    authorize_url = github_oauth_service.get_authorize_url()
    return RedirectResponse(url=authorize_url)


@router.get("/extOauthYandex.requestSignin")
async def method_ext_oauth_yandex_request_signin() -> JSONResponse:
    """OAuth with external OAuth Yandex provider."""

    settings = get_settings()

    if not settings.auth_ext_oauth_yandex_enabled:
        return api_error(
            ApiErrorCode.API_FORBIDDEN,
            "Yandex OAuth currently disabled by server administrators.",
        )

    yandex_oauth_service = YandexOauthService(
        client_id=settings.auth_ext_oauth_yandex_client_id,
        client_secret=settings.auth_ext_oauth_yandex_client_secret,
        client_redirect_uri=settings.auth_ext_oauth_yandex_redirect_uri,
    )

    authorize_url = yandex_oauth_service.get_authorize_url()
    return RedirectResponse(url=authorize_url)
