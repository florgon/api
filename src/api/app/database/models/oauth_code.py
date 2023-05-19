"""
    OAuth code session database model.
"""

# Core model base.
from app.database.core import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
# ORM.
from sqlalchemy.sql import func


class OAuthCode(Base):
    """OAuth code session (window)"""

    __tablename__ = "oauth_codes"

    # Database.
    # will be reworked.
    id = Column(Integer, primary_key=True, index=True, nullable=False)

    # Bindance.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("oauth_clients.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("user_sessions.id"), nullable=False)

    # Will be reworked.
    was_used = Column(Boolean, default=False)

    # Time.
    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
