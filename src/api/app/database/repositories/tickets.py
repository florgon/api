"""
   Tickets repository.
"""


from app.database.repositories.base import BaseRepository
from app.database.models.ticket import Ticket


class TicketsRepository(BaseRepository):
    """
    Tickets database CRUD repository.
    """

    def create(
        self,
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
        Creates new ticket object that ready to use and have all required stuff (as secret) generated.
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

        self.finish(ticket)
        return ticket
