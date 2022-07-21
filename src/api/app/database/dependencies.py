"""
    FastAPI dependencies
"""

# For importing Session from dependencies!
# Do not remove.
from sqlalchemy.ext.asyncio import AsyncSession, async_session  # noqa # pylint: disable=unused-import

# Importing session.
from .core import SessionLocal, sessionmaker


async def get_db() -> sessionmaker:
    """Session getter for database. Used as dependency for database itself."""
    async with async_session() as db_session:
        db_session: AsyncSession = db_session
        try:
            yield db_session
        finally:
            db_session.close()
    #db_session = SessionLocal()
    #try:
    #    yield db_session
    #finally:
    #    db_session.close()
