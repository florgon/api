"""
    Blog database model.
"""

# ORM.
from sqlalchemy.sql import func
from sqlalchemy import Integer, Column, DateTime, Text, String, ForeignKey

# Core model base.
from app.database.core import Base


class BlogPost(Base):
    """Blog post model"""

    __tablename__ = "blog_posts"

    # Database.
    id = Column(Integer, primary_key=True, index=True, nullable=False)

    # Author id.
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Post.
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    # Times.
    time_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())