"""
    Social OAuth router.
    Provides API methods (routes) for working with Social accounts OAuth.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse


from app.services.api.response import api_error
from app.services.api.errors import ApiErrorCode


router = APIRouter()


@router.get("/extSocialAuthVk.signin")
async def method_ext_social_auth_vk_signin() -> JSONResponse:
    """ OAuth with social VK provider. """

    return api_error(ApiErrorCode.API_NOT_IMPLEMENTED, "VK OAuth not implemented yet")


@router.get("/extSocialAuthGithub.signin")
async def method_ext_social_auth_github_signin() -> JSONResponse:
    """ OAuth with social GitHub provider. """

    return api_error(ApiErrorCode.API_NOT_IMPLEMENTED, "GitHub OAuth not implemented yet")


@router.get("/extSocialAuthYandex.signin")
async def method_ext_social_auth_github_signin() -> JSONResponse:
    """ OAuth with social Yandex provider. """

    return api_error(ApiErrorCode.API_NOT_IMPLEMENTED, "Yandex OAuth not implemented yet")
