"""
    Database environment settings.
    
    Currently, database SHOULD be only PostgreSQL and there is no plans to migrate or allow to change provider.
"""

from typing import Literal, Any
from functools import lru_cache

from pydantic import BaseSettings


class DatabaseSettings(BaseSettings):
    """
    Configuration for the database (PostgreSQL).
    """

    name: str = "database"
    user: str = "postgres"
    password: str = "postgres"
    host: str = "localhost"
    port: int = 5432

    orm_echo_statements: bool = False
    orm_echo_statements_debug: bool = False

    orm_create_all: bool = True
    orm_max_overflow: int = 0
    orm_poll_pre_ping: bool = True
    orm_pool_recycle: int = 3600
    orm_pool_timeout: int = 10
    orm_poll_size: int = 20

    class Config:
        env_prefix = "POSTGRES_DB_"

    @property
    def orm_engine_kwargs(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "echo": self.echo,
            "pool_size": self.orm_poll_size,
            "max_overflow": self.orm_max_overflow,
            "pool_timeout": self.orm_pool_timeout,
            "pool_recycle": self.orm_pool_recycle,
            "pool_pre_ping": self.orm_poll_pre_ping,
        }

    @property
    def echo(self) -> bool | Literal["debug"]:
        if self.orm_echo_statements:
            return "debug" if self.orm_echo_statements_debug else True
        return False

    @property
    def url(self) -> str:
        return f"postgresql://{self._connection_string()}"

    @property
    def async_url(self) -> str:
        return f"postgresql+asyncpg://{self._connection_string()}"

    def _connection_string(self) -> str:
        return f"{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@lru_cache(maxsize=1)
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()
