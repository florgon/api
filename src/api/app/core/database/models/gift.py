"""
    Gift database model.
"""

from enum import IntEnum

# Core model base.
from app.core.database.core import Base

# ORM.
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func


class Gift(Base):
    """Gift model"""

    __tablename__ = "gifts"

    id = Column(Integer, primary_key=True, index=True, nullable=False)

    # Code to accept gift.
    promocode = Column(String, nullable=False, unique=True)

    max_uses = Column(Integer, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    reward = Column(Integer, nullable=False)  # GiftRewardType

    is_active = Column(Boolean, nullable=False, default=True)
    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class GiftRewardType(IntEnum):
    """Reward types for the gift."""

    VIP = 1
