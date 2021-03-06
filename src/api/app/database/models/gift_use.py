"""
    Gift use database model.
"""

# ORM.
from sqlalchemy import ForeignKey, Integer, Column, DateTime
from sqlalchemy.sql import func

# Core model base.
from app.database.core import Base


class GiftUse(Base):
    """Gift use"""

    __tablename__ = "gifts_uses"

    id = Column(Integer, primary_key=True, index=True, nullable=False)

    gift_id = Column(Integer, ForeignKey("gifts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
