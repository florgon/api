"""
    Serializers for Ticket model.
"""
from typing import Any

from app.database.models.ticket import Ticket


def serialize_ticket(ticket: Ticket, *, in_list: bool = False) -> dict[str, Any]:
    """
    Serializes single ticket or ticket as list item, if in_list is True.
    """
    serialized = {
        "id": ticket.id,
        "first_name": ticket.full_name,
        "last_name": ticket.last_name,
        "middle_name": ticket.middle_name,
        "subject": ticket.subject,
        "email": ticket.email,
        "phone_number": ticket.phone_number,
        "user_id": None,
        "text": ticket.text,
    }
    if serialized["user_id"]:
        serialized["user_id"] = ticket.user_id
    else:
        serialized.pop("user_id")

    return serialized if in_list else {"ticket": serialized}


def serialize_tickets(tickets: list[Ticket]) -> dict[str, Any]:
    """
    Serializes list of tickets.
    """
    return {"tickets": [serialize_ticket(ticket, in_list=True) for ticket in tickets]}
