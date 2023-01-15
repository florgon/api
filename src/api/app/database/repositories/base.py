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
        if not isinstance(self.db, Session):
            raise TypeError(
                f"`db` should be database Session! Expected session but got: {type(self.db)}"
            )
