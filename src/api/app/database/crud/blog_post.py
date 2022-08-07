# pylint: disable=singleton-comparison
"""
    Blog post CRUD utils for the database.
"""

# Services.
from app.database.models.blog_post import BlogPost

# Libraries.
from sqlalchemy.orm import Session


def get_by_id(db: Session, post_id: int) -> BlogPost | None:
    """Returns post by it`s ID."""
    return db.query(BlogPost).filter(BlogPost.id == post_id).first()


def get_by_author_id(db: Session, author_id: int) -> list[BlogPost]:
    """Returns posts by it`s owner ID."""
    return db.query(BlogPost).filter(BlogPost.author_id == author_id).all()


def get_all(db: Session) -> list[BlogPost]:
    """Returns all posts."""
    return db.query(BlogPost).all()


def create(db: Session, author_id: int, title: str, content: str) -> BlogPost:
    """Creates post"""

    # Create new Post.
    post = BlogPost(author_id=author_id, title=title, content=content)

    # Apply Post in the database.
    db.add(post)
    db.commit()
    db.refresh(post)

    return post
