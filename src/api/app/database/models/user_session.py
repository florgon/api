"""
    User session database model.
"""

# Core model base.
from app.database.core import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
# ORM.
from sqlalchemy.sql import func


class UserSession(Base):
    """Auth service user session model"""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    token_secret = Column(String, nullable=False)

    ip_address = Column(String(12), nullable=False)
    user_agent_id = Column(Integer, ForeignKey("user_agents.id"), nullable=False)
    geo_country = Column(String(2), nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)

    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
