"""
    Publication database model.
"""

# ORM.
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Integer, Column, Text, DateTime

# Core model base.
from app.database.core import Base


class Publication(Base):
    """User publication model"""

    __tablename__ = "user_publications"

    # Access data.
    id = Column(Integer, primary_key=True, index=True, nullable=False)

    # Display data.
    text = Column(Text, nullable=False)

    # User who wrote this publication.
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())