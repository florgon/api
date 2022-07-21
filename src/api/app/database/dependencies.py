"""
    FastAPI dependencies
"""

# For importing Session from dependencies!
# Do not remove.
from sqlalchemy.orm import Session  # noqa # pylint: disable=unused-import

# Importing session.
from .core import SessionLocal, sessionmaker


def get_db() -> sessionmaker:
    """Session getter for database. Used as dependency for database itself."""
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
