from app.config import Settings
from app.database.dependencies import Session
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error

from fastapi import Request


def oauth_password_grant(
    req: Request, client_id: int, client_secret: str, db: Session, settings: Settings
):
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED,
        "Password grant type is not implemented! (And will be not implemented soon).",
    )
