"""
    User database model.
"""

# ORM.
from sqlalchemy import (
    Integer, String, Column
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
