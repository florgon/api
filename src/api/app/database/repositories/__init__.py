"""
    Database models CRUD repositores.

    For now there is migration in process!
    Not all covered with new Repositories (uses CRUD).
"""
from .users import UsersRepository
from .oauth_clients import OAuthClientsRepository
from .gifts import GiftsRepository
from .base import BaseRepository

__all__ = [
    "BaseRepository",
    "UsersRepository",
    "OAuthClientsRepository",
    "GiftsRepository",
]
