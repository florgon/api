"""
    External OAuth providers service.
"""

from .providers import YandexOauthService, VkOauthService, GithubOauthService
from .builders import (
    build_yandex_oauth_service,
    build_vk_oauth_service,
    build_github_oauth_service,
)

__all__ = [
    "YandexOauthService",
    "GithubOauthService",
    "VkOauthService",
    "build_github_oauth_service",
    "build_vk_oauth_service",
    "build_yandex_oauth_service",
]
