"""
    Database models CRUD repositores.
"""

from .users import UsersRepository
from .user_sessions import UserSessionsRepository
from .user_agent import UserAgentsRepository
from .tickets import TicketsRepository
from .oauth_code import OAuthCodesRepository
from .oauth_clients import OAuthClientsRepository
from .oauth_client_user import OAuthClientUserRepository
from .oauth_client_use import OAuthClientUseRepository
from .base import BaseRepository

__all__ = [
    "BaseRepository",
    "UsersRepository",
    "OAuthClientsRepository",
    "UserSessionsRepository",
    "TicketsRepository",
    "UserAgentsRepository",
    "OAuthClientUserRepository",
    "OAuthClientUseRepository",
    "OAuthCodesRepository",
]
