"""
    Blog API router.
    Provides API methods (routes) for working blog.
"""

# Database.
from app.database import crud
from app.database.dependencies import Session, get_db
from app.serializers.blog_post import serialize as serialize_post
from app.serializers.blog_post import serialize_list as serialize_posts

# Etc.
from app.services.api.response import ApiErrorCode, api_error, api_success
from app.services.limiter.depends import RateLimiter
from app.services.permissions import Permission
from app.services.request import query_auth_data_from_request
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/blog.create", dependencies=[Depends(RateLimiter(times=2, minutes=5))])
async def method_blog_create(
    title: str, content: str, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Creates new blog post."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.admin]
    )

    if not auth_data.user.is_admin:
        return api_error(
            ApiErrorCode.API_FORBIDDEN,
            "You are not an administrator, and forbidden to create a new blog post!",
        )

    post = crud.blog_post.create(
        db, author_id=auth_data.user.id, title=title, content=content
    )
    if post:
        return api_success(serialize_post(post, in_list=False))
    return api_error(ApiErrorCode.API_UNKNOWN_ERROR, "Failed to create post.")


@router.get("/blog.get", dependencies=[Depends(RateLimiter(times=3, seconds=1))])
async def method_blog_get(
    post_id: int | None = None,
    author_id: int | None = None,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Returns specific post by ID or all posts."""

    # There is some weird logic, if there is will be SQL I may try to do joins,
    # or even also rework API solution...
    # If you don`t get me, forgot.

    if post_id is None:
        # All posts (no post_id passed)
        if author_id is not None:
            posts = crud.blog_post.get_by_author_id(db, author_id=author_id)
        else:
            posts = crud.blog_post.get_all(db)
        authors = crud.user.get_by_ids(db, user_ids=[post.author_id for post in posts])
        return api_success(serialize_posts(posts=posts, authors=authors))

    post = crud.blog_post.get_by_id(db, post_id)
    if post is None:
        return api_error(
            ApiErrorCode.API_ITEM_NOT_FOUND, "Post with given ID not found!"
        )

    author = crud.user.get_by_id(db, user_id=post.author_id)
    return api_success(serialize_post(post=post, author=author, in_list=False))
