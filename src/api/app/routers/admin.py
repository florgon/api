"""
    Admin API router.
    Provides API methods (routes) for working with admin stuff.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.services.permissions import Permission
from app.services.request import query_auth_data_from_request
from app.services.api.response import api_success
from app.database import crud

from app.database.dependencies import get_db, Session

router = APIRouter()

@router.get("/admin.getSessionCounters")
async def method_admin_get_sessions(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns session counters."""
    query_auth_data_from_request(req, db, required_permissions=[Permission.admin])
    return api_success(
        {
            "sessions": {
                "active": crud.user_session.get_active_count(db),
                "active_grouped": crud.user_session.get_active_count_grouped(db)
            }
        }
    )
