"""
    FastAPI dependencies for the database.
"""

from typing import TypeVar, Callable

from sqlalchemy.orm import Session
from fastapi import Depends

from .core import sessionmaker, SessionLocal

T = TypeVar("T")


def get_db() -> sessionmaker:
    """
    Returns database session for making plain database requests.
    Notice: Should be slowly moved inside abstraction layer (like, repositories)
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


def get_repository(repo_type: type[T]) -> Callable[[Session], T]:
    """
    Instantiates repository dependency (wrapped) based on type.
    (Returns function that instantiates repository with given type)
    """

    def wrapper(db: Session = Depends(get_db)) -> T:
        return repo_type(db)

    return wrapper
