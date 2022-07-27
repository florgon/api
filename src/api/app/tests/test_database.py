import pytest

from fastapi.testclient import TestClient

from app.app import app
from app.database.core import SessionLocal

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_database_sql_select(client):
    expected = 32
    with SessionLocal() as session:
        assert session.execute(f"SELECT {expected};") == expected
