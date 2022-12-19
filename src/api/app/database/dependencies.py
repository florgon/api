"""
    FastAPI dependencies
"""

from typing import Type, Callable
from sqlalchemy.orm import Session
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
    """
    Returns repository dependency (wrapped) with database getter dependency.
    """

    def get_repo(db: Session = Depends(get_db)) -> Type[BaseRepository]:
        """
        Dependency itself.
        """
        return repo_type(db)

    return get_repo
