"""
    User linked accounts database model.
"""

from sqlalchemy.sql import func
from sqlalchemy import String, Integer, ForeignKey, DateTime, Column

from app.database.core import Base


class UserLinkedAccounts(Base):
    """
    Model with all user linked accounts (OAuth external accounts).
    Used for searching authorized user by account.
    """

    __tablename__ = "user_linked_accounts"

    # Database.
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # External services user IDs.
    # (There is email field for convience and can be ommited).
    vk_user_id = Column(Integer, nullable=True)
    vk_user_email = Column(String, nullable=True)
    github_user_id = Column(Integer, nullable=True)
    github_user_email = Column(String, nullable=True)
    yandex_user_id = Column(Integer, nullable=True)
    yandex_user_email = Column(String, nullable=True)

    # Times.
    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
