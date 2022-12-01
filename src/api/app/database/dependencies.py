"""
    FastAPI dependencies
"""

from typing import Type, Callable

# For importing Session from dependencies!
# Do not remove.
from sqlalchemy.orm import Session  # noqa # pylint: disable=unused-import
from fastapi import Depends
from .core import SessionLocal, sessionmaker
from .repositories.base import BaseRepository


def get_db() -> sessionmaker:
    """Session getter for database. Used as dependency for database itself."""
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


def get_repository(repo_type: Type[BaseRepository]) -> Callable:
    def get_repo(db: Session = Depends(get_db)) -> Type[BaseRepository]:
        return repo_type(db)

    return get_repo
