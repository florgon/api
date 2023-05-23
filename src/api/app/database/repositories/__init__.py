"""
    Database models CRUD repositores.

    For now there is migration in process!
    Not all covered with new Repositories (uses CRUD).
"""
from .base import BaseRepository
from .gifts import GiftsRepository
from .oauth_clients import OAuthClientsRepository
from .users import UsersRepository

__all__ = [
    "BaseRepository",
    "UsersRepository",
    "OAuthClientsRepository",
    "GiftsRepository",
]
