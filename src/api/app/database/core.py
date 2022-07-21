"""
    Database core. Contains engine, ORM related stuff.
"""

# Imports.
import asyncio
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Settings.
from app.config import Settings

# Database engine.
engine = create_async_engine(url=Settings().database_url,
                       pool_size=20, 
                       max_overflow=0, 
                       pool_recycle=3600, 
                       poolclass=QueuePool
)
metadata = MetaData(bind=engine)

# Base, session from core.
SessionLocal = sessionmaker(
    class_=AsyncSession,
    autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(metadata=metadata)


async def create_all():
    """Creates all database metadata."""
    async with engine.begin() as connection:
        # await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        # metadata.create_all(bind=engine)

def create_all_sync():
    loop = asyncio.get_running_loop()
    loop.run_until_complete(create_all())