"""
    Base repository.
"""
from app.database.dependencies import Session


class BaseRepository:
    """
    Base abstract class for repositories.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
