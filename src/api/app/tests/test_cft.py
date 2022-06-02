import unittest
import time

from app.services.cftokens import generate_cft


class TestCFTokensUnit(unittest.TestCase):
    def test_timed(self):
        secret = "mysecret"
        salt = "mysalt"
        payload = "Hello, world!"

        cft_a = generate_cft(payload, secret, salt)
        time.sleep(1)
        cft_b = generate_cft(payload, secret, salt)

        self.assertNotEqual(cft_a, cft_b)

    def test_conifrmation(self):
        pass  # confirm_cft

    def test_link(self):
        pass  # generate_confirmation_link
