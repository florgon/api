"""
    OAuth client use database model.
"""

# ORM.
from sqlalchemy.sql import func
from sqlalchemy import Integer, ForeignKey, DateTime, Column

# Core model base.
from app.database.core import Base


class OAuthClientUse(Base):
    """Auth service OAuth2 client usage statistics model"""

    __tablename__ = "oauth_clients_uses"

    # Database.
    id = Column(Integer, primary_key=True, index=True, nullable=False)

    # Use data.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("oauth_clients.id"), nullable=False)

    # Time.
    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
