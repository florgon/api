"""
    Blog post database model serializer.
"""

import time

from app.core.database.models.blog_post import BlogPost


def serialize(post: BlogPost, in_list: bool = False) -> dict:
    """Returns dict object for API response with serialized blog post data."""

    serialized_post = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "created_at": time.mktime(post.time_created.timetuple()),
    }

    if in_list:
        return serialized_post

    return {"post": serialized_post}


def serialize_list(posts: list[BlogPost]) -> dict:
    """Returns dict object for API response with serialized blog post list data."""

    serialized_posts = [serialize(post) for post in posts]
    return {"posts": serialized_posts}


serialize_posts = serialize_list
serialize_post = serialize
