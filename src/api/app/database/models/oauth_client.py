"""
    OAuth client database model.
"""

from sqlalchemy.sql import func
from sqlalchemy import String, Integer, ForeignKey, DateTime, Column, Boolean
from app.database.core import Base


class OAuthClient(Base):
    """Auth service OAuth2 client model"""

    __tablename__ = "oauth_clients"

    # Access data.
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    secret = Column(String, nullable=False)

    # Display data.
    display_name = Column(String, nullable=False)
    display_avatar = Column(String, nullable=True)

    # User who owns this client.
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Means is client deactivated or not.
    is_active = Column(Boolean, nullable=False, default=True)

    # Means is client verified by administrators (allow access to direct auth later)
    is_verified = Column(Boolean, nullable=False, default=False)

    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    time_verified = Column(DateTime(timezone=True), nullable=True)
