"""
    Database core. 
    Contains engine and ORM related stuff.
"""

from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy import create_engine, MetaData
from app.config import get_logger, get_database_settings

engine = create_engine(
    **get_database_settings().orm_engine_kwargs,
    poolclass=QueuePool,
)
metadata = MetaData(bind=engine)
Base: type = declarative_base(metadata=metadata)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=True, bind=engine
)


def create_all() -> None:
    """
    Creating all database metadata.
    Currently there is only ORM metadata builder.
    !TODO: Migrations with alembic.
    """
    if not get_database_settings().orm_create_all:
        return
    try:
        metadata.create_all(bind=engine)
    except (IntegrityError, OperationalError) as e:
        get_logger().error(
            f"[database_core] Failed to do `create_all` as metadata raised: `{e}`"
        )
