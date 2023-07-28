"""
    Database models CRUD repositores.
    
    !TODO!: This architecture of CRUD repositores is pretty weird, complicated and bad:
    There is some way of reordering that.
"""

from .users import UsersRepository
from .user_sessions import UserSessionsRepository
from .oauth_clients import OAuthClientsRepository
from .gifts import GiftsRepository
from .base import BaseRepository

__all__ = [
    "BaseRepository",
    "UsersRepository",
    "OAuthClientsRepository",
    "GiftsRepository",
    "UserSessionsRepository",
]
