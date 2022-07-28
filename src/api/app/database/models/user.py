"""
    User database model.
"""

# ORM.
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, Column, Boolean, DateTime, Text

# Core model base.
from app.database.core import Base


class User(Base):
    """Auth service user model"""

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
    is_admin = Column(Boolean, nullable=False, default=False)
    is_vip = Column(Boolean, nullable=False, default=False)

    # Privacy.
    privacy_profile_public = Column(Boolean, nullable=False, default=True)
    privacy_profile_require_auth = Column(Boolean, nullable=False, default=False)

    # Security.
    security_tfa_enabled = Column(Boolean, nullable=False, default=False)
    security_tfa_secret_key = Column(String, nullable=True, default=None)

    # Public profile.
    profile_bio = Column(Text, nullable=True)
    profile_website = Column(String, nullable=True)
    profile_social_username_vk = Column(String, nullable=True)
    profile_social_username_tg = Column(String, nullable=True)
    profile_social_username_gh = Column(String, nullable=True)

    # Times.
    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    time_verified = Column(DateTime(timezone=True), nullable=True)

    def is_female(self) -> bool:
        """Returns is current user female of not."""
        return self.sex is False

    def get_mention(self) -> str:
        """Returns user mention for email."""
        if self.first_name:
            return f"{self.first_name}"
        return f"@{self.username}"
