"""
    Browser user agent repository.
"""

from app.database.repositories.base import BaseRepository
from app.database.models.user_agent import UserAgent


class UserAgentsRepository(BaseRepository):
    """
    Browser user agent CRUD repository.
    """

    def get_by_string(self, user_agent_string: str) -> UserAgent | None:
        """Returns user agent by it`s string."""
        user_agent = (
            self.db.query(UserAgent)
            .filter(UserAgent.user_agent == user_agent_string)
            .first()
        )
        return user_agent

    def get_by_id(self, user_agent_id: int) -> UserAgent | None:
        """Returns user agent by it`s id."""
        return self.db.query(UserAgent).filter(UserAgent.id == user_agent_id).first()

    def get_or_create_by_string(self, user_agent_string: str) -> UserAgent:
        """Creates or returns already created user agent."""
        user_agent = self.get_by_string(user_agent_string)
        if user_agent is None:
            user_agent = UserAgent(user_agent=user_agent_string)
            self.finish(user_agent)
        return user_agent
