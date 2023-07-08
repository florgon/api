"""
    Base abstract repository.
"""
from abc import ABCMeta

from app.database.dependencies import Session


class BaseRepository(metaclass=ABCMeta):
    """
    Base abstract class for repositories.
    """

    db: Session

    def __init__(self, db: Session) -> None:
        """
        Initialize a repository with a given database session.
        """
        self.db = db
        if not isinstance(self.db, Session):
            raise TypeError(
                f"`db` should be database Session! Expected session but got: {type(self.db)}"
            )

    def finish(self, instance: object) -> None:
        """
        Finishes instance with adding and commiting it.
        TODO: Research this method.
        """
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
