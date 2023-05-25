"""
    Tests database connection with database core.
"""

import unittest

from app.database.core import SessionLocal
from sqlalchemy import text


class TestDatabaseUnit(unittest.TestCase):
    """Check database unit (SQL)"""

    def test_database_sql_select(self):
        """Checks that SQL SELECT equals to argument number."""
        expected = 32
        with SessionLocal() as session:
            actual = session.execute(text(f"SELECT {expected}")).fetchall()[0][0]
            self.assertEqual(actual, expected)
