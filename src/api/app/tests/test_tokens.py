import unittest

from app.tokens.access_token import AccessToken


class TestAccessTokenUnit(unittest.TestCase):
    def test_access_token_unsigned(self):
        key = "my_secret_key"
        token = AccessToken("me", 1, 2, 3, "", key=key)

        decoded_unsigned_token = AccessToken.decode(token.encode())
        self.assertFalse(decoded_unsigned_token.signature_is_valid())

        decoded_signed_token = AccessToken.decode(token.encode(), key=key)
        self.assertTrue(decoded_signed_token.signature_is_valid())

        self.assertEqual(
            decoded_unsigned_token.get_subject(), decoded_signed_token.get_subject()
        )
        self.assertEqual(
            decoded_unsigned_token.get_session_id(),
            decoded_signed_token.get_session_id(),
        )

    def test_access_token(self):
        key = "my_secret_key"
        token = AccessToken("me", 1, 2, 3, "", key=key)
        encoded_token = token.encode()
        decoded_token = AccessToken.decode(encoded_token, key)
        self.assertEqual(
            AccessToken.decode(encoded_token, key).get_raw_payload(),
            decoded_token.get_raw_payload(),
        )
