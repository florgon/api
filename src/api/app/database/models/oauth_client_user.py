"""
    OAuth client user (linked oauth client to user) database model.
"""

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime, Column, Boolean

from app.database.core import Base


class OAuthClientUser(Base):
    """Auth service OAuth2 client linked user model"""

    __tablename__ = "oauth_clients_users"

    # Database.
    id = Column(Integer, primary_key=True, index=True, nullable=False)

    # Link data.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("oauth_clients.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    requested_scope = Column(String, default="", nullable=False)
    oauth_client = relationship("OAuthClient")

    # Time.
    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
