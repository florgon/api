"""
    Gift use CRUD utils for the database.
"""

# Models.
from app.database.models.gift_use import GiftUse

# Libraries.
from sqlalchemy.orm import Session


def create(db: Session, user_id: int, gift_id: int) -> GiftUse:
    """Creates new Gift use object that is committed in the database already."""
    gift_use = GiftUse(user_id=user_id, gift_id=gift_id)
    db.add(gift_use)
    db.commit()
    db.refresh(gift_use)
    return gift_use


def get_unique_uses(db: Session, gift_id: int) -> int:
    """Returns count of all uses of gift by different users."""
    return (
        db.query(GiftUse.user_id)
        .filter(GiftUse.gift_id == gift_id)
        .group_by(GiftUse.user_id)
        .count()
    )


def get_uses(db: Session, gift_id: int) -> int:
    """Returns total count of gift uses overall."""
    return db.query(GiftUse).filter(GiftUse.gift_id == gift_id).count()
