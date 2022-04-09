"""
    User database model.
"""

# ORM.
from sqlalchemy.sql import func
from sqlalchemy import (
    Integer, String, Column, Boolean, DateTime
)

# Core model base.
from ..core import Base


class User(Base):
    """ Auth service user model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    password = Column(String, nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)

    time_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    time_verified = Column(DateTime(timezone=True), nullable=True)

