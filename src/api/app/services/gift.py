from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.database.repositories import GiftsRepository
from app.database.models.user import User
from app.database.models.gift import GiftRewardType, Gift
from app.database.dependencies import Session
from app.database import crud


def _query_gift(gifts_repo: GiftsRepository, promocode: str) -> Gift:
    """
    Queries gift by promocode, which is active and can be used for any user (except validations by reward type).
    """
    gift = gifts_repo.get_by_promocode(promocode=promocode) if promocode else None
    if not gift:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST, "Gift not found, or invalid promocode."
        )

    if crud.gift_use.get_uses(gifts_repo.db, gift.id) >= gift.max_uses:
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
    if gift.reward not in [GiftRewardType.VIP]:
        raise ApiErrorException(
            ApiErrorCode.GIFT_CANNOT_ACCEPTED,
            "Gift cannot be accepted due to outdated reward type.",
        )

    if gift.reward == GiftRewardType.VIP:
        if user.is_vip:
            raise ApiErrorException(
                ApiErrorCode.GIFT_CANNOT_ACCEPTED,
                "Gift cannot be accepted due to you already being a vip.",
            )
        user.is_vip = True
        gift_use = crud.gift_use.create(db, user.id, gift.id)
        db.add(user)
        db.add(gift_use)
        db.commit()


def query_and_accept_gift(
    gifts_repo: GiftsRepository, acceptor: User, promocode: str
) -> None:
    """
    Queries and accepts gift by promocode if it is active and valid.
    """
    gift = _query_gift(gifts_repo=gifts_repo, promocode=promocode)
    _apply_gift(gifts_repo.db, gift, acceptor)
