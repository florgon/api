"""
    Gift database model.
"""

from enum import IntEnum

# ORM.
from sqlalchemy import String, Integer, Column, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func

# Core model base.
from app.database.core import Base


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
    VIP = 1
