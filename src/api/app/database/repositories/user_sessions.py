"""
    User sessions repository.
"""


from typing import Iterator, Iterable

from app.database.repositories.base import BaseRepository
from app.database.models.user_session import UserSession


class UserSessionsRepository(BaseRepository):
    """
    User sessions database CRUD repository.
    """

    def deactivate_one(self, session: UserSession, *, commit=True) -> None:
        """
        Deactivate one user session (mark as inactive) and commit by default.
        """
        session.is_active = False  # type: ignore

        # Finish database instance.
        self.db.add(session)
        if commit:
            self.commit()

    def deactivate_list(
        self, sessions: Iterable[UserSession] | Iterator[UserSession], *, commit=True
    ) -> None:
        """
        Deactivates list of user sessions (mark as inactive) and commit by default.
        """
        for session in sessions:
            self.deactivate_one(session, commit=False)
        if commit:
            self.db.commit()

    def get_by_owner_id(self, owner_id: int, active_only=True) -> list[UserSession]:
        """Returns list of sessions by owner user id."""
        query = self.db.query(UserSession).filter(UserSession.owner_id == owner_id)
        query = query.filter(UserSession.is_active == True) if active_only else query
        return query.all()

    def get_by_id(self, session_id: int) -> UserSession | None:
        """Returns session by ID"""
        return self.db.query(UserSession).filter(UserSession.id == session_id).first()
