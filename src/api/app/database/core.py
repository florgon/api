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
settings = Settings()
engine = create_engine(url=settings.database_url,
                       pool_size=settings.database_pool_size, 
                       max_overflow=settings.database_pool_size * 2, 
                       pool_recycle=-1, 
                       poolclass=QueuePool
)
metadata = MetaData(bind=engine)

# Base, session from core.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(metadata=metadata)


def create_all():
    """Creates all database metadata."""
    metadata.create_all(bind=engine)
