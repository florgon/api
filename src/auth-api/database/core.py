"""
    Database core. Contains engine, ORM related stuff.
"""

# Imports.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database engine.
engine = create_engine("postgresql://auth-api:postgres@database/auth-api")  # TODO.

# Base, session from core.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_all():
    """Creatas all database metadata. """
    Base.metadata.create_all(bind=engine)
