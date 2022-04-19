"""
    User database model.
"""

# ORM.
from sqlalchemy.sql import func
from sqlalchemy import (
    ForeignKey, Integer, String, Column, Boolean, DateTime
)

# Core model base.
from app.database.core import Base


class OAuthClient(Base):
    """ Auth service OAuth2 client model"""
    __tablename__ = "oauth_clients"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    secret = Column(String, unique=True, index=True, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Means is client deactivated or not.
    is_active = Column(Boolean, nullable=False, default=True)

    # Means is client verified by administrators (allow access to direct auth later)
    is_verified = Column(Boolean, nullable=False, default=True)

    time_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    time_verified = Column(DateTime(timezone=True), nullable=True)
