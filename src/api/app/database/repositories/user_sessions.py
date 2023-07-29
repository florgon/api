"""
    User sessions repository.
"""

import secrets
from typing import Iterator, Iterable

from app.database.repositories.user_agent import UserAgentsRepository, UserAgent
from app.database.repositories.base import BaseRepository
from app.database.models.user_session import UserSession


class UserSessionsRepository(BaseRepository):
    """
    User sessions database CRUD repository.
    """

    @staticmethod
    def generate_secret() -> str:
        """
        Generate standartized secret key for the new client.
        """
        return secrets.token_urlsafe(32)

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

    def get_by_ip_address_and_user_agent(
        self, ip_address: str, user_agent: UserAgent
    ) -> UserSession | None:
        """Returns session by ip address and user agent."""
        return (
            self.db.query(UserSession)
            .filter(UserSession.ip_address == ip_address)
            .filter(UserSession.user_agent_id == user_agent.id)
            .filter(UserSession.is_active == True)
            .first()
        )

    def get_by_ip_address(
        self, ip_address: str, active_only: bool = False, limit: int = -1
    ) -> list[UserSession]:
        """Returns session by ip address."""
        query = self.db.query(UserSession).filter(UserSession.ip_address == ip_address)
        query = query.filter(UserSession.is_active == True) if active_only else query
        query = query.limit(limit) if limit >= 1 else query

        return query.all()

    def get_or_create_new(
        self,
        owner_id: int,
        client_host: str,
        client_user_agent: str,
        client_geo_country: str | None = None,
    ) -> UserSession:
        """Returns user session or creates a new one."""

        user_agent = UserAgentsRepository(self.db).get_or_create_by_string(
            client_user_agent
        )
        user_agent_id = user_agent.id

        queried_session = self.get_by_ip_address_and_user_agent(client_host, user_agent)
        if queried_session and queried_session.owner_id == owner_id:
            return queried_session

        # Create new user session.
        session_token_secret = self.generate_secret()
        session = UserSession(
            owner_id=owner_id,
            token_secret=session_token_secret,
            ip_address=client_host,
            user_agent_id=user_agent_id,
            geo_country=client_geo_country or "",  # TODO: nullable.
        )

        self.finish(session)
        return session
