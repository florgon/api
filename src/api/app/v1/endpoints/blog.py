"""
    Blog API router.
    Provides API methods (routes) for working blog.
"""

# Database.
from app.core.database import crud
from app.core.database.dependencies import Session, get_db
from app.core.serializers.blog_post import serialize as serialize_post
from app.core.serializers.blog_post import serialize_list as serialize_posts

# Etc.
from app.core.services.api.response import ApiErrorCode, api_error, api_success
from app.core.services.limiter.depends import RateLimiter
from app.core.services.permissions import Permission
from app.core.services.request import query_auth_data_from_request
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get(
    "/blog/posts/create", dependencies=[Depends(RateLimiter(times=2, minutes=5))]
)
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


@router.get("/blog/posts", dependencies=[Depends(RateLimiter(times=3, seconds=1))])
async def method_blog_posts_get(
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Returns all blog posts."""
    posts = crud.blog_post.get_all(db)
    return api_success(serialize_posts(posts=posts))


@router.get(
    "/blog/posts/{post_id}", dependencies=[Depends(RateLimiter(times=3, seconds=1))]
)
async def method_blog_get(
    post_id: int,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Returns specific post by ID."""

    post = crud.blog_post.get_by_id(db, post_id)
    if post is None:
        return api_error(
            ApiErrorCode.API_ITEM_NOT_FOUND, "Post with given ID not found!"
        )

    return api_success(serialize_post(post, in_list=False))
