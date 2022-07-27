"""
    Gift API router.
    Provides API methods (routes) for working gifts.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.services.api.response import api_success, api_error, ApiErrorCode

from app.services.request import query_auth_data_from_request

from app.database.dependencies import get_db, Session
from app.database.models.gift import GiftRewardType
from app.config import get_settings, Settings
from app.database import crud

router = APIRouter()


@router.get("/gift.accept")
async def method_gift_accept(
    req: Request,
    db: Session = Depends(get_db),
    promocode: str | None = None,
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Accepts gift."""

    auth_data = query_auth_data_from_request(req, db)
    gift = crud.gift.get_by_promocode(db, promocode=promocode) if promocode else None
    if not gift:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST, "Gift not found, or invalid promocode."
        )

    if crud.gift_use.get_uses(db, gift.id) >= gift.max_uses:
        return api_error(ApiErrorCode.GIFT_USED, "Gift already used max times.")

    if not gift.is_active:
        return api_error(ApiErrorCode.GIFT_EXPIRED, "Gift not active or expired.")
    if gift.reward == GiftRewardType.VIP:
        if auth_data.user.is_vip:
            return api_error(
                ApiErrorCode.GIFT_CANNOT_ACCEPTED,
                "Gift cannot be accepted due to you already being a vip.",
            )
        user = auth_data.user
        user.is_vip = True
    else:
        return api_error(
            ApiErrorCode.GIFT_CANNOT_ACCEPTED,
            "Gift cannot be accepted due to outdated reward type.",
        )
    gift_use = crud.gift_use.create(db, user.id, gift.id)
    db.add(user)
    db.add(gift_use)

    db.commit()

    return api_success({"gift": {"status": "accepted"}})
