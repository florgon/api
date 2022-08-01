"""
    Social OAuth router.
    Provides API methods (routes) for working with Social accounts OAuth.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error
from app.services.ext_social_auth.github_esa import GithubOauthService
from app.services.ext_social_auth.vk_esa import VkOauthService
from app.services.ext_social_auth.yandex_esa import YandexOauthService

router = APIRouter()


@router.get("/extSocialAuthVk.signin")
async def method_ext_social_auth_vk_signin() -> JSONResponse:
    """OAuth with social VK provider."""

    VkOauthService()
    return api_error(ApiErrorCode.API_NOT_IMPLEMENTED, "VK OAuth not implemented yet")


@router.get("/extSocialAuthGithub.signin")
async def method_ext_social_auth_github_signin() -> JSONResponse:
    """OAuth with social GitHub provider."""

    GithubOauthService()
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED, "GitHub OAuth not implemented yet"
    )


@router.get("/extSocialAuthYandex.signin")
async def method_ext_social_auth_yandex_signin() -> JSONResponse:
    """OAuth with social Yandex provider."""

    YandexOauthService()
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED, "Yandex OAuth not implemented yet"
    )
