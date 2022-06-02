import unittest
import time
from app.services.jwt import encode, decode
from app.services.api.errors import ApiErrorException

class _TestUser(object):
    id: int
    def __init__(self, id: int):
        self.id = id


class TestJWTokensUnit(unittest.TestCase):
    def test_contains_default_payload(self):
        encoded_token = encode(_TestUser(1), {}, "", 0, "")
        decoded_token = decode(encoded_token, "", _token_type="")

        self.assertIn("iss", decoded_token)
        self.assertIn("sub", decoded_token)
        self.assertIn("iat", decoded_token)
        self.assertNotIn("exp", decoded_token)

        encoded_token = encode(_TestUser(1), {}, "", 1, "")
        decoded_token = decode(encoded_token, "", _token_type="")

        self.assertIn("exp", decoded_token)

    def test_default_payload(self):
        user = _TestUser(1)
        iss = "pytest"
        ttl = 32

        encoded_token = encode(user, {}, iss, ttl, "")
        decoded_token = decode(encoded_token, "", _token_type="")

        self.assertEqual(decoded_token["iss"], iss)
        self.assertEqual(decoded_token["exp"], decoded_token["iat"] + ttl)
        self.assertEqual(decoded_token["sub"], user.id)
    
    def test_custom_payload(self):
        user = _TestUser(1)
        payload = {"mypayloadfield": "Hello, World!"}

        encoded_token = encode(user, payload, "", 0, "")
        decoded_token = decode(encoded_token, "", _token_type="")

        self.assertIn("mypayloadfield", decoded_token)

    def test_expiration(self):
        user = _TestUser(1)

        encoded_token = encode(user, {}, "", 1, "")
        decode(encoded_token, "", _token_type="")
        time.sleep(2)
        with self.assertRaises(ApiErrorException):
            decode(encoded_token, "", _token_type="")

    def test_custom_secret(self):
        user = _TestUser(1)
        secret = "mycoolsecret"

        encoded_token = encode(user, {}, "", 0, secret)
        decoded_token = decode(encoded_token, secret, _token_type="")

        self.assertEqual(decoded_token["sub"], user.id)