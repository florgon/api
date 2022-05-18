"""
    User database model.
"""

# ORM.
from sqlalchemy.sql import func
from sqlalchemy import (
    Integer, String, Column, Boolean, DateTime
)

# Core model base.
from app.database.core import Base


class User(Base):
    """ Auth service user model"""
    __tablename__ = "users"

    # Database.
    id = Column(Integer, primary_key=True, index=True, nullable=False)


    # Sensitive information.
    email = Column(String, unique=True, index=True, nullable=False)

    # Display.
    username = Column(String, unique=True, index=True, nullable=False)
    avatar = Column(String, nullable=True)

    # Name.
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    # Other.
    sex = Column(Boolean, nullable=False, default=False)
    
    # Password.
    password = Column(String, nullable=False)
    
    # States.
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)

    # Times.
    time_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    time_verified = Column(DateTime(timezone=True), nullable=True)

    def is_female(self) -> bool:
        return self.sex == False