"""
    Blog post database model serializer.
"""

import time

from app.database.models.blog_post import BlogPost
from app.database.models.user import User


def serialize(post: BlogPost, author: User, in_list: bool = False) -> dict:
    """Returns dict object for API response with serialized blog post data."""

    serialized_post = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": {"id": author.id, "username": author.username},
        "created_at": time.mktime(post.time_created.timetuple()),
    }

    if in_list:
        return serialized_post

    return {"post": serialized_post}


def serialize_list(posts: list[BlogPost], authors: list[User]) -> dict:
    """Returns dict object for API response with serialized blog post list data."""

    serialized_posts = [serialize(post, author) for post, author in zip(posts, authors)]
    return {"posts": serialized_posts}


serialize_posts = serialize_list
serialize_post = serialize
