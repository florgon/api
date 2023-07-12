"""
    Database model for Request.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database.core import Base


class Offer(Base):
    __tablename__ = 'offers'
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    text = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String(18), nullable=False)
    full_name = Column(String, nullable=False)

    # Time
    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
