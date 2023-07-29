"""
    CRUD module for Ticket model.
"""

from sqlalchemy.orm import Session

from api.app.database.models.ticket import Ticket


def create(
    db: Session,
    text: str,
    first_name: str,
    phone_number: str,
    email: str,
    subject: str,
    middle_name: str,
    last_name: str,
    user_id: int | None = None,
) -> Ticket:
    """
    Creates ticket in database and returns it.
    """
    ticket = Ticket(
        text=text,
        first_name=first_name,
        subject=subject,
        middle_name=middle_name,
        last_name=last_name,
        phone_number=phone_number,
        email=email,
        user_id=user_id,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def get_all(db: Session) -> list[Ticket]:
    """
    Returns a list of all tickets.
    """
    return db.query(Ticket).all()


def get_by_id(db: Session, id: int) -> OffTicketer | None:
    """
    Returns single ticket by id or None if ticket is not found.
    """
    return db.query(Ticket).filter(Ticket.id == id).first()
