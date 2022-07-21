"""
    Upload API router.
    Provides API methods (routes) for working with uploading files (images).
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.services.request import query_auth_data_from_request
from app.services.api.response import api_success
from app.services.limiter.depends import RateLimiter

from app.database.dependencies import get_db, Session

router = APIRouter()


@router.get("/upload.getAvatarUploadServer")
async def method_user_get_info(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns user account information."""
    await RateLimiter(times=2, seconds=15)
    auth_data = query_auth_data_from_request(req, db, required_permissions=None)
    user_id = auth_data.user.id
    return api_success({
        "upload_url": f"https://cdnus0.florgon.space/upload?rid=0&uid={user_id}&ft=avatar"
    })

