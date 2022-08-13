"""
    OAuth client use database model.
"""

# Core model base.
from app.core.database.core import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer

# ORM.
from sqlalchemy.sql import func


class OAuthClientUse(Base):
    """Auth service OAuth2 client usage statistics model"""

    __tablename__ = "oauth_clients_uses"

    # Database.
    id = Column(Integer, primary_key=True, index=True, nullable=False)

    # Use data.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Time.
    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
