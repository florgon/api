"""
    External OAuth router.
    Provides API methods (routes) for working with social accounts OAuth.
"""
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import APIRouter
from app.services.ext_oauth import (
    build_yandex_oauth_service,
    build_vk_oauth_service,
    build_github_oauth_service,
)
from app.services.api.response import api_success, api_error
from app.services.api.errors import ApiErrorCode

router = APIRouter(include_in_schema=False)


@router.get("/extOauthVk.requestSignin")
async def method_ext_oauth_vk_request_signin(display: str = "page") -> JSONResponse:
    """OAuth with external OAuth VK provider."""

    authorize_url = build_vk_oauth_service(display).get_authorize_url()
    return RedirectResponse(url=authorize_url)


@router.get("/extOauthGithub.requestSignin")
async def method_ext_oauth_github_request_signin() -> JSONResponse:
    """OAuth with external OAuth GitHub provider."""

    authorize_url = build_github_oauth_service().get_authorize_url()
    return RedirectResponse(url=authorize_url)


@router.get("/extOauthYandex.requestSignin")
async def method_ext_oauth_yandex_request_signin() -> JSONResponse:
    """OAuth with external OAuth Yandex provider."""

    authorize_url = build_yandex_oauth_service().get_authorize_url()
    return RedirectResponse(url=authorize_url)


@router.get("/extOauthVk.resolveSignin")
async def method_ext_oauth_vk_signin_with_code(code: str) -> JSONResponse:
    """OAuth with external OAuth VK provider."""

    resolver_response = build_vk_oauth_service().resolve_code(code=code)
    if resolver_response is None:
        return api_error(
            ApiErrorCode.API_UNKNOWN_ERROR,
            "Code resolver respond with unexpected data!",
        )

    return api_success({"resolver_response": resolver_response})


@router.get("/extOauthGitHub.resolveSignin")
async def method_ext_oauth_github_signin_with_code(code: str) -> JSONResponse:
    """OAuth with external OAuth GitHub provider."""

    resolver_response = build_github_oauth_service().resolve_code(code=code)
    if resolver_response is None:
        return api_error(
            ApiErrorCode.API_UNKNOWN_ERROR,
            "Code resolver respond with unexpected data!",
        )

    return api_success({"resolver_response": resolver_response})


@router.get("/extOauthYandex.resolveSignin")
async def method_ext_oauth_yandex_signin_with_code(code: str) -> JSONResponse:
    """OAuth with external OAuth Yandex provider."""

    resolver_response = build_yandex_oauth_service().resolve_code(code=code)
    if resolver_response is None:
        return api_error(
            ApiErrorCode.API_UNKNOWN_ERROR,
            "Code resolver respond with unexpected data!",
        )

    return api_success({"resolver_response": resolver_response})
