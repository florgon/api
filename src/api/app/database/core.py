"""
    Database core. Contains engine, ORM related stuff.
"""

# Imports.
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Settings.
from app.config import Settings

# Database engine.
engine = create_engine(url=Settings().database_url,
                       pool_size=20, 
                       max_overflow=0, 
                       pool_recycle=3600, 
                       poolclass=QueuePool
)
metadata = MetaData(bind=engine)

# Base, session from core.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(metadata=metadata)


def create_all():
    """Creates all database metadata."""
    metadata.create_all(bind=engine)
