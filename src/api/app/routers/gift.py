"""
    Gift API router.
    Provides API methods (routes) for working gifts.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from app.database import crud
from app.database.dependencies import Session, get_db
from app.database.models.gift import Gift, GiftRewardType
from app.database.models.user import User
from app.services.api.response import api_success
from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.services.request import query_auth_data_from_request
from app.services.limiter.depends import RateLimiter


router = APIRouter()


def _query_gift(db: Session, promocode: str) -> Gift:
    gift = crud.gift.get_by_promocode(db, promocode=promocode) if promocode else None
    if not gift:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST, "Gift not found, or invalid promocode."
        )

    if crud.gift_use.get_uses(db, gift.id) >= gift.max_uses:
        raise ApiErrorException(ApiErrorCode.GIFT_USED, "Gift already used max times.")

    if not gift.is_active:
        raise ApiErrorException(
            ApiErrorCode.GIFT_EXPIRED, "Gift not active or expired."
        )

    return gift


def _apply_gift(db: Session, gift: Gift, user: User) -> None:
    """
    Applies gift to the user.
    """
    if gift.reward == GiftRewardType.VIP:
        if user.is_vip:
            raise ApiErrorException(
                ApiErrorCode.GIFT_CANNOT_ACCEPTED,
                "Gift cannot be accepted due to you already being a vip.",
            )
        user = user
        user.is_vip = True
    else:
        raise ApiErrorException(
            ApiErrorCode.GIFT_CANNOT_ACCEPTED,
            "Gift cannot be accepted due to outdated reward type.",
        )

    gift_use = crud.gift_use.create(db, user.id, gift.id)
    db.add(user)
    db.add(gift_use)
    db.commit()


@router.get("/gift.accept")
async def method_gift_accept(
    req: Request,
    db: Session = Depends(get_db),
    promocode: str | None = None,
) -> JSONResponse:
    """Accepts gift."""

    user = query_auth_data_from_request(req, db).user
    await RateLimiter(times=10, minutes=5).check(req)

    gift = _query_gift(db=db, promocode=promocode)
    _apply_gift(db, gift, user)

    return api_success({"gift": {"status": "accepted"}})
