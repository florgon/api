"""
    Database core. Contains engine, ORM related stuff.
"""

# Imports.
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Settings.
from app.config import Settings

# Database engine.
engine = create_engine(Settings().database_url)
metadata = MetaData(bind=engine)

# Base, session from core.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(metadata=metadata)

def create_all():
    """Creatas all database metadata. """
    metadata.create_all(bind=engine)
