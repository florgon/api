"""
    User database model.
"""

from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Text, String, Integer, DateTime, Column, Boolean
from app.database.core import Base


class User(Base):
    """Auth service user model"""

    __tablename__ = "users"

    # Database.
    id = Column(Integer, primary_key=True, index=True, nullable=False)

    # Sensitive information.
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String(18), nullable=True, unique=True)

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
    security_hash_method = Column(Integer, default=0, nullable=False)

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
    time_online = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    time_verified = Column(DateTime(timezone=True), nullable=True)

    def is_female(self) -> bool:
        """Returns is current user female of not."""
        return self.sex is False

    def get_mention(self) -> str:
        """Returns user mention for email."""
        return f"{self.first_name}" if self.first_name else f"@{self.username}"

    @hybrid_property
    def full_name(self) -> str:
        """
        Returns fullname based on first and last name as property.
        """
        if self.first_name is not None:
            if self.last_name is None:
                return self.first_name
            else:
                return f"{self.first_name} {self.last_name}"
        return f"{self.last_name}" if self.last_name is not None else ""
