"""
    Database core. Contains engine, ORM related stuff.
"""

# Settings.
from app.config import Settings

# Imports.
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Database engine.
settings = Settings()
engine = create_engine(
    url=settings.database_dsn,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_recycle=settings.database_pool_recycle,
    poolclass=QueuePool,
)
metadata = MetaData(bind=engine)

# Base, session from core.
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=True, bind=engine
)
Base = declarative_base(metadata=metadata)


def create_all():
    """Creates all database metadata."""
    metadata.create_all(bind=engine)
