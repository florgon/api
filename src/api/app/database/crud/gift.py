"""
    Gift CRUD utils for the database.
"""

# Libraries.
import secrets
from sqlalchemy.orm import Session

# Models.
from app.database.models.gift import Gift, GiftRewardType


def create(db: Session, reward_type: GiftRewardType, created_by: int, max_uses: int) -> Gift:
    promocode = _generate_promocode(32)
    gift = Gift(promocode=promocode, created_by=created_by, max_uses=max_uses, reward=reward_type.value)
    db.add(gift)
    db.commit()
    db.refresh(gift)
    return gift


def get_by_promocode(db: Session, promocode: str) -> Gift | None:
    return (
        db.query(Gift).filter(Gift.promocode == promocode).first()
    )


def _generate_promocode(size: int) -> str:
    """Returns a random string for promocode."""
    return secrets.token_urlsafe(nbytes=size)