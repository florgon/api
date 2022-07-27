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

router = APIRouter()


@router.get("/upload.getPhotoUploadServer")
async def method_upload_get_photo_upload_server(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns upload url for uploading photo (image) and then save for using as user avatar or OAuth client avatar."""
    await RateLimiter(times=2, seconds=30).check(req)

    query_auth_data_from_request(req, db, required_permissions=None)

    settings = get_settings()
    upload_server_domain = settings.upload_server_domain
    return api_success({"upload_url": f"http://{upload_server_domain}/upload"})


@router.get("/upload.saveOauthClientAvatar")
async def method_upload_save_oauth_client_avatar(
    photo: str, client_id: int, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Updates OAuth client avatar with photo uploaded in photo upload server ."""
    await RateLimiter(times=2, minutes=30).check(req)

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

    is_updated = False
    if oauth_client.display_avatar != photo:
        oauth_client.display_avatar = photo
        db.add(oauth_client)
        db.commit()

    return api_success({"photo_url": photo, "updated": is_updated})
