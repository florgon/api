"""
    Upload API router.
    Provides API methods (routes) for working with uploading files.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.services.request import query_auth_data_from_request
from app.services.api.response import api_success, api_error, ApiErrorCode
from app.services.limiter.depends import RateLimiter

from app.database.dependencies import get_db, Session
from app.database import crud
from app.config import get_settings
from app.services.permissions import Permission

router = APIRouter()


@router.get("/upload.getPhotoUploadServer")
async def method_upload_get_photo_upload_server(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns upload url for uploading photo (image) and then save for using as user avatar or OAuth client avatar."""
    await RateLimiter(times=2, seconds=30).check(req)

    query_auth_data_from_request(req, db, required_permissions=None)

    settings = get_settings()
    upload_server_domain = "cdnus0.florgon.space"
    return api_success({"upload_url": f"http://{upload_server_domain}/upload"})


@router.get("/upload.saveOauthClientAvatar")
async def method_upload_save_oauth_client_avatar(
    photo: str, client_id: int, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Updates OAuth client avatar with photo uploaded in photo upload server ."""

    # TODO:
    # Notice that is not clear implementation of uploading mechanism.
    # As next implementation have real check that uploading is done by upload server.

    auth_data = query_auth_data_from_request(req, db, required_permissions=None)
    oauth_client = crud.oauth_client.get_by_id(db, client_id=client_id)
    if not oauth_client:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found.")
    if oauth_client.owner_id != auth_data.user.id:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_FORBIDDEN,
            "You are not owner of this OAuth client.",
        )
    await RateLimiter(times=2, minutes=30).check(req)

    # TODO: Add config settings, allow only upload server subdomain.
    if not urlsplit(photo).netloc.endswith("florgon.space"):
        return api_error(
            ApiErrorCode.API_FORBIDDEN,
            "Denied to upload user avatar from non Florgon domain!",
        )

    is_updated = False
    if oauth_client.display_avatar != photo:
        oauth_client.display_avatar = photo
        db.add(oauth_client)
        db.commit()
        is_updated = True

    return api_success({"photo_url": photo, "is_updated": is_updated})


from urllib.parse import urlsplit


@router.get("/upload.saveUserAvatar")
async def method_upload_save_user_avatar(
    photo: str, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Updates current user avatar with photo uploaded in photo upload server ."""

    # TODO:
    # Notice that is not clear implementation of uploading mechanism.
    # As next implementation have real check that uploading is done by upload server.

    auth_data = query_auth_data_from_request(
        req, db, required_permissions=Permission.edit
    )
    await RateLimiter(times=2, minutes=30).check(req)

    # TODO: Add config settings, allow only upload server subdomain.
    if not urlsplit(photo).netloc.endswith("florgon.space"):
        return api_error(
            ApiErrorCode.API_FORBIDDEN,
            "Denied to upload user avatar from non Florgon domain!",
        )

    is_updated = False
    user = auth_data.user
    if user.avatar != photo:
        user.avatar = photo
        db.add(user)
        db.commit()
        is_updated = True

    return api_success({"photo_url": photo, "is_updated": is_updated})
