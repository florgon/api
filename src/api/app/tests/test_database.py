import pytest

from fastapi.testclient import TestClient

from app.app import app
from app.database.dependencies import get_db, Session

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_database_sql_select(client):
    db = get_db()
    expected = 32
    with db.begin() as session:
        session: Session = session
        assert session.execute(f"SELECT {expected};") == expected
