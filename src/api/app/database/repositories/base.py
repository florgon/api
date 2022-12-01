from app.database.dependencies import Session


class BaseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db
