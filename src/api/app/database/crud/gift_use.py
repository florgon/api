"""
    Gift use CRUD utils for the database.
"""

# Libraries.
from sqlalchemy.orm import Session

# Models.
from app.database.models.gift_use import GiftUse


def create(db: Session, user_id: int, gift_id: int) -> GiftUse:
    gift_use = GiftUse(user_id=user_id, gift_id=gift_id)
    db.add(gift_use)
    db.commit()
    db.refresh(gift_use)
    return gift_use


def get_unique_uses(db: Session, gift_id: int) -> int:
    return (
        db.query(GiftUse.user_id)
        .filter(GiftUse.gift_id == gift_id)
        .group_by(GiftUse.user_id)
        .count()
    )


def get_uses(db: Session, gift_id: int) -> int:
    return db.query(GiftUse).filter(GiftUse.gift_id == gift_id).count()
