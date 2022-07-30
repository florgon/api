import unittest

from app.services.passwords import check_password, get_hashed_password


class TestPasswordsUnit(unittest.TestCase):
    def test_passwords(self):
        test_password = "mypassword"
        with self.assertRaises(TypeError):
            check_password(32, 64)  # noqa
        self.assertTrue(
            check_password(test_password, get_hashed_password(test_password))
        )
        self.assertEqual(
            get_hashed_password(test_password), get_hashed_password(test_password)
        )
