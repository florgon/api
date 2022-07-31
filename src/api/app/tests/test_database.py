import pytest
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.app import app
from app.database.core import SessionLocal


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestDatabaseUnit(unittest.TestCase):
    def test_database_sql_select(self):
        expected = 32
        with SessionLocal() as session:
            actual = session.execute(text(f"SELECT {expected}")).fetchall()[0][0]
            self.assertEqual(actual, expected)
