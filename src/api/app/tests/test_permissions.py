"""
    Tests OAuth scope permissions unit (parsing, normalization).
"""

import unittest

from app.services.permissions import (
    parse_permissions_from_scope,
    normalize_scope,
    Permission,
)


class TestPermissionsUnit(unittest.TestCase):
    """Checks OAuth scope permissions unit."""

    def test_normalization(self):
        """Tests scope normalization."""
        with self.assertRaises(TypeError):
            normalize_scope({Permission.email})  # noqa
        self.assertEqual(normalize_scope(""), "")
        self.assertEqual(normalize_scope("email"), "email")
        self.assertEqual(normalize_scope("email,  email"), "email")
        self.assertEqual(normalize_scope("\nemail, \remail"), "")

    def test_parse(self):
        """Checking main parsing feature (scope to permissions list)."""
        with self.assertRaises(TypeError):
            parse_permissions_from_scope({Permission.email})  # noqa
        self.assertIsInstance(parse_permissions_from_scope(""), set)
        self.assertEqual(parse_permissions_from_scope(""), set())
        self.assertEqual(parse_permissions_from_scope("email"), {Permission.email})
        self.assertEqual(
            parse_permissions_from_scope("email,  email"), {Permission.email}
        )
        self.assertEqual(parse_permissions_from_scope("\nemail, \remail"), set())
        self.assertTrue(Permission.email in parse_permissions_from_scope("*"))
