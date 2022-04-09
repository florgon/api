"""
    Database core. Contains engine, ORM related stuff.
"""

# Imports.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Engine.
connection_url = "postgresql://auth-api:postgres@database/auth-api"
engine = create_engine(connection_url)

# Base, session from core.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_all():
    """Creatas all database metadata. """
    Base.metadata.create_all(bind=engine)
