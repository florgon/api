"""
    OAuth client use database model.
"""

from sqlalchemy.sql import func
from sqlalchemy import Integer, ForeignKey, DateTime, Column
from app.database.core import Base


class OAuthClientUse(Base):
    """Auth service OAuth2 client usage statistics model"""

    __tablename__ = "oauth_clients_uses"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("oauth_clients.id"), nullable=False)
    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
