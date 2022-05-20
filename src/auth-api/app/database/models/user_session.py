"""
    User session database model.
"""

# ORM.
from sqlalchemy.sql import func
from sqlalchemy import (
    ForeignKey, Integer, Column, DateTime, String
)

# Core model base.
from app.database.core import Base


class UserSession(Base):
    """ Auth service user session model"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    token_secret = Column(String, nullable=False)
    
    time_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)