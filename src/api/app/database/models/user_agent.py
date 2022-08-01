"""
    User agent database model.
"""

# ORM.
from sqlalchemy import Column, Integer, Text

# Core model base.
from app.database.core import Base


class UserAgent(Base):
    """Auth service client user agent string model"""

    __tablename__ = "user_agents"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_agent = Column(Text, nullable=False)
