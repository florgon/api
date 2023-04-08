"""
    Database core. Contains engine, ORM related stuff.
"""

from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError, IntegrityError

# Imports.
from sqlalchemy import create_engine, MetaData

# Settings.
from app.config import get_logger, Settings

# Database engine.
settings = Settings()
engine = create_engine(
    url=settings.database_dsn,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_recycle=settings.database_pool_recycle,
    poolclass=QueuePool,
    pool_pre_ping=True,
)
metadata = MetaData(bind=engine)

# Base, session from core.
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=True, bind=engine
)
Base = declarative_base(metadata=metadata)


def create_all():
    """Creates all database metadata."""
    try:
        metadata.create_all(bind=engine)
    except (IntegrityError, OperationalError) as e:
        get_logger().error(
            f"[database_core] Failed to do `create_all` as metadata returned `{e}`"
        )
