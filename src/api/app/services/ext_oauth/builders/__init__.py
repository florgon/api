"""
    Builders for OAuth services instances.
"""

from yandex_builder import build_yandex_oauth_service
from vk_builder import build_vk_oauth_service
from github_builder import build_github_oauth_service

__all__ = [
    "build_yandex_oauth_service",
    "build_vk_oauth_service",
    "build_github_oauth_service",
]
