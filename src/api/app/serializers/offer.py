"""
    Serializers for Offer model.
"""
from typing import Any

from app.database.models.offer import Offer


def serialize_offer(offer: Offer, *, in_list: bool = False) -> dict[str, Any]:
    """
    Serializes single offer or offer as list item, if in_list is True.
    """
    serialized = {
        "id": offer.id,
        "full_name": offer.full_name,
        "email": offer.email,
        "phone_number": offer.phone_number,
        "user_id": None,
        "text": offer.text,
    }
    if serialized["user_id"]:
        serialized["user_id"] = offer.user_id
    else:
        serialized.pop("user_id")

    return serialized if in_list else {"offer": serialized}


def serialize_offers(offers: list[Offer]) -> dict[str, Any]:
    """
    Serializes list of offers.
    """
    return {"offers": [serialize_offer(offer, in_list=True) for offer in offers]}
