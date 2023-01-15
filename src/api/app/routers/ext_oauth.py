"""
    External OAuth router.
    Provides API methods (routes) for working with social accounts OAuth.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import get_settings
from app.database import crud
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error, api_success
from app.services.ext_oauth.github_provider import GithubOauthService
from app.services.ext_oauth.vk_provider import VkOauthService
from app.services.ext_oauth.yandex_provider import YandexOauthService

router = APIRouter()


def _build_vk_oauth_service(vk_oauth_display: str | None = None) -> VkOauthService:
    """
    Returns VK OAuth provider (service).
    """
    settings = get_settings()

    if not settings.auth_ext_oauth_vk_enabled:
        return api_error(
            ApiErrorCode.API_FORBIDDEN,
            "VK OAuth currently disabled by server administrators.",
        )

    return VkOauthService(
        client_id=settings.auth_ext_oauth_vk_client_id,
        client_secret=settings.auth_ext_oauth_vk_client_secret,
        client_redirect_uri=settings.auth_ext_oauth_vk_redirect_uri,
        display=vk_oauth_display,
    )


def _build_yandex_oauth_service() -> YandexOauthService:
    """
    Returns Yandex OAuth provider (service).
    """
    settings = get_settings()

    if not settings.auth_ext_oauth_yandex_enabled:
        return api_error(
            ApiErrorCode.API_FORBIDDEN,
            "Yandex OAuth currently disabled by server administrators.",
        )

    return YandexOauthService(
        client_id=settings.auth_ext_oauth_yandex_client_id,
        client_secret=settings.auth_ext_oauth_yandex_client_secret,
        client_redirect_uri=settings.auth_ext_oauth_yandex_redirect_uri,
        login_hint="",
        force_confirm=True,
    )


def _build_github_oauth_service() -> GithubOauthService:
    """
    Returns GitHub OAuth provider (service).
    """
    settings = get_settings()

    if not settings.auth_ext_oauth_github_enabled:
        return api_error(
            ApiErrorCode.API_FORBIDDEN,
            "GitHub OAuth currently disabled by server administrators.",
        )

    return GithubOauthService(
        client_id=settings.auth_ext_oauth_github_client_id,
        client_secret=settings.auth_ext_oauth_github_client_secret,
        client_redirect_uri=settings.auth_ext_oauth_github_redirect_uri,
    )


@router.get("/extOauthVk.requestSignin")
async def method_ext_oauth_vk_request_signin(display: str = "page") -> JSONResponse:
    """OAuth with external OAuth VK provider."""

    authorize_url = _build_vk_oauth_service(display).get_authorize_url()
    return RedirectResponse(url=authorize_url)


@router.get("/extOauthGithub.requestSignin")
async def method_ext_oauth_github_request_signin() -> JSONResponse:
    """OAuth with external OAuth GitHub provider."""

    authorize_url = _build_github_oauth_service().get_authorize_url()
    return RedirectResponse(url=authorize_url)


@router.get("/extOauthYandex.requestSignin")
async def method_ext_oauth_yandex_request_signin() -> JSONResponse:
    """OAuth with external OAuth Yandex provider."""

    authorize_url = _build_yandex_oauth_service().get_authorize_url()
    return RedirectResponse(url=authorize_url)


@router.get("/extOauthVk.resolveSignin")
async def method_ext_oauth_vk_signin_with_code(code: str) -> JSONResponse:
    """OAuth with external OAuth VK provider."""

    resolver_response = _build_vk_oauth_service().resolve_code(code=code)
    if resolver_response is None:
        return api_error(
            ApiErrorCode.API_UNKNOWN_ERROR,
            "Code resolver respond with unexpected data!",
        )

    return api_success({"resolver_response": resolver_response})


@router.get("/extOauthGitHub.resolveSignin")
async def method_ext_oauth_vk_signin_with_code(code: str) -> JSONResponse:
    """OAuth with external OAuth GitHub provider."""

    resolver_response = _build_github_oauth_service().resolve_code(code=code)
    if resolver_response is None:
        return api_error(
            ApiErrorCode.API_UNKNOWN_ERROR,
            "Code resolver respond with unexpected data!",
        )

    return api_success({"resolver_response": resolver_response})


@router.get("/extOauthYandex.resolveSignin")
async def method_ext_oauth_yandex_signin_with_code(code: str) -> JSONResponse:
    """OAuth with external OAuth Yandex provider."""

    resolver_response = _build_yandex_oauth_service().resolve_code(code=code)
    if resolver_response is None:
        return api_error(
            ApiErrorCode.API_UNKNOWN_ERROR,
            "Code resolver respond with unexpected data!",
        )

    return api_success({"resolver_response": resolver_response})
