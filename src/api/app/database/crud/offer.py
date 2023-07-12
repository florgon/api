"""
    CRUD module for Offer model.
"""

from sqlalchemy.orm import Session

from app.database.models.offer import Offer


def create(
    db: Session,
    text: str,
    full_name: str,
    phone_number: str,
    email: str,
    user_id: int | None = None,
) -> Offer:
    """
    Creates offer in database and returns it.
    """
    offer = Offer(
        text=text,
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        user_id=user_id,
    )

    db.add(offer)
    db.commit()
    db.refresh(offer)

    return offer


def get_list(db: Session) -> list[Offer]:
    """
    Returns a list of all offers.
    """
    return db.query(Offer).all()
