"""
    FastAPI dependencies
"""

# For importing Session from dependecies, not sqlalchemy.
from sqlalchemy.orm import Session

# Importing session.
from .core import (
    SessionLocal,
    sessionmaker
)

def get_db() -> sessionmaker:
    """Session getter for database. Used as dependency for database itself. """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
