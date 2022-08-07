# pylint: disable=singleton-comparison
"""
    Gift CRUD utils for the database.
"""

import secrets
from app.database.models.gift import Gift, GiftRewardType
from sqlalchemy.orm import Session


def create(
    db: Session, reward_type: GiftRewardType, created_by: int, max_uses: int
) -> Gift:
    """Creates new Gift object that is committed in the database already and have all required stuff (as promocode) generated."""
    promocode = _generate_promocode(32)
    gift = Gift(
        promocode=promocode,
        created_by=created_by,
        max_uses=max_uses,
        reward=reward_type.value,
    )
    db.add(gift)
    db.commit()
    db.refresh(gift)
    return gift


def get_by_promocode(db: Session, promocode: str) -> Gift | None:
    """Returns Gift by it`s promocode string."""
    return db.query(Gift).filter(Gift.promocode == promocode).first()


def _generate_promocode(size: int) -> str:
    """Returns a random string for promocode."""
    return secrets.token_urlsafe(nbytes=size)
