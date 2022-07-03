"""
    Florgon API base token class implementation.

    Provides base class for tokens,
    Some sort of abstract class.
"""

import jwt  # Library with base JWT implementation.
import time  # Utils for expiration dates.

from . import exceptions


class _Token(object):
    """
    Florgon API token implementation.

    Some sort of Abstract class that represents any Token
    (For example, Access, Session or whatever token you want).

    All tokens should be children of this class.

    To implement token, inherit from this class and implement own token implementation:
        custom fields,
        override encode / decode methods with injecting own payload,
        update token type.

    Notice that updating token type is very important, because core implementation based on
    token type validation, which means that there is no way
    to inject another type of token into another type of token.

    Specifications: Implements JWT (JSON Web Token) as abstract class.
    """

    # Token payload without BASE token fields (your own payload or payload).
    # Being set when decoding token and this data will be WRITTEN encoding token
    # (as custom payload in additional to base).
    # You should use this field with injecting own fields there on overriding token encoding.
    custom_payload: dict = {}

    # JWT signing algorithm. Used by JWT library to sign tokens.
    # May be: HS(256|384|512) for HMAC SHA,
    # or one of crypto algorithms: RSA/EC/RSAPSS/OKPA.
    # Notice that using asymmetric algorithm is more secure but not implemented yet.
    _signing_algorithm: str = "HS256"

    # Totally raw token payload, being set when decoding token (should be empty with encoding operation),
    # should be used when you are want to get some raw information about decoded token.
    # (Notice that all fields should be under protected fields!)
    _raw_payload: dict | None = None

    # If token was decoded without checking the signature (due to some reason),
    # The token will be marked as invalid signature.
    _signature_is_valid: bool = True

    # Token additional headers (JWT headers), not supposed to use mostly.
    _custom_headers: dict = {}

    # Secret key for signing actual token.
    # Should not be modified directly as it will be updated automatically.
    _key: str | None = None

    # Core type of the token.
    # Should be individual for each token class, as there is validation for token type,
    # and core would not allow you to inject another type of token into another token type.
    # SHOULD BE OVERRIDDEN IN CHILDREN CLASSES.
    _type: str = ""  # Will fail when encoding token.

    # Base token fields.
    # Set when decoding token, and will be encoded when encoding token.
    _ttl: int | float = 1.0  # Token expiration time in seconds (Time-To-Live, TTL)
    _issuer: str = None  # The issuer of the token (hostname).
    _subject: int = None  # Subject of the token (ID of the object (User))

    # When decoded token was issued and expires.
    _expires_at: float = 0
    _issued_at: float = 0

    def get_key(self) -> str | None:
        """Returns secret key or None if not set."""
        return self._key

    def set_key(self, key: str | None) -> None:
        """Sets secret key or removes it."""
        assert isinstance(
            key, str | None
        ), "Key must be a string or None for clearing the key"
        self._key = key

    def get_raw_payload(self) -> dict | None:
        """Returns raw payload of decoded token or None if token was not decoded."""
        return self._raw_payload

    @classmethod
    def get_type(cls) -> str:
        """Returns token type for internal check, not supposed to be used so much."""
        return cls._type

    def get_payload(self) -> dict:
        """Returns custom token payload from decoded payload or custom injection."""
        return self.custom_payload

    def get_subject(self) -> int:
        """Returns subject of token as ID."""
        return self._subject

    def get_issued_at(self) -> float:
        """Returns when decoded token was issued."""
        return self._issued_at

    def get_expires_at(self) -> float:
        """Returns when decoded token will expire."""
        return self._expires_at

    def signature_is_valid(self) -> bool:
        """Returns true if token was decoded with checking the signature."""
        return self._signature_is_valid

    def encode(self, *, key: str | None = None):
        """
        Encodes token into JWT string.

        You are supposed to inherit inside own class and
        implement at your own using super().encode() call.

        Example:
        ```
            self.custom_payload["myfield"] = self._custom_field
            super().encode()
        ```
        """

        # Setter for key.
        if self._key is None:
            if key is None:
                assert (
                    False
                ), "You must specify either field `key` or pass a `key` param when encoding token!"
            self._key = key

        # Type should be set to custom token type.
        if not self._type:
            assert (
                False
            ), "For encoding you supposed to specify custom token type inside inherited class"

        # Arguments.
        assert isinstance(self._key, str), "Key should be a string"
        assert isinstance(self._subject, int), "Unexpected subject data type!"
        assert isinstance(self._issuer, str), "Unexpected issuer data type!"
        assert self._ttl >= 0, "Token TTL must be unsigned integer >= 0!"

        # Get current time as time, when token was issued,
        # for IAT field and calculating EXP field with TTL.
        issued_at = time.time()

        # Generate payload.
        payload = {
            # JWT base payload.
            "typ": self._type,  # This is not JWT format, means type of token based on custom APPLICATION level.
            "iss": self._issuer,
            "sub": self._subject,
            "iat": issued_at,
            # Custom payload.
            **self.custom_payload,
        }

        if self._ttl > 0:
            # If time-to-live (TTL) is not null,
            # set token expiration date, which is constructed by
            # time when token was created (now) (timestamp, in seconds) and adding it TTL in seconds.
            payload["exp"] = issued_at + self._ttl

        # Encoding final JWT for payload/headers with secret key.
        token = jwt.encode(
            key=self._key,
            payload=payload,
            headers=self._custom_headers,
            algorithm=self._signing_algorithm,
            json_encoder=None,
        )
        return token

    @classmethod
    def decode(cls, token: str, key: str | None = None):
        """
        Decodes token from JWT string.

        You are supposed to inherit inside own class and
        implement at your own using super().decode() call.

        Example:
        ```
            instance = super().decode(token, payload)
            instance._custom_field = "myfield"
            return instance
        ```
        """

        # Decoding token.
        payload = cls._decode_payload(token, key)

        # Get token time-to-live (TTL).
        issued_at = float(payload["iat"])
        ttl, expires_at = 0, 0  # By default token does not has TTL (No expiration).
        if "exp" in payload:
            # If there is expiration date,
            # calculate TTL based on expiration timestamp minus issued timestamp.
            expires_at = float(payload["exp"])
            ttl = expires_at - issued_at

        # Base class instance.
        issuer = payload["iss"]
        subject = payload["sub"]
        instance = cls(issuer, ttl, subject, key=None)

        # Injecting custom fields.
        instance.custom_payload = payload.copy()
        instance._raw_payload = payload
        instance._issued_at = issued_at
        instance._expires_at = expires_at
        instance._signature_is_valid = key is not None

        # Deleting base fields from custom payload.
        del instance.custom_payload["iss"]
        del instance.custom_payload["sub"]
        del instance.custom_payload["iat"]
        del instance.custom_payload["typ"]
        if ttl != 0:
            del instance.custom_payload["exp"]

        return instance

    @classmethod
    def decode_unsigned(cls, token: str):
        """
        Decodes unsigned (unverified) token.
        Will cause _signature_is_valid (get_signature_is_valid()) to be false,
        as token signature is not verified.
        """
        return cls.decode(token=token, key=None)

    @classmethod
    def _decode_payload(
        cls,
        token: str,
        key: str | None = None,
        *,
        _always_verify_signature: bool = False,
    ):
        """
        Decodes token from JWT string and returns it RAW payload.

        :param _always_verify_signature: if True, will always verify signature even when key is none.
        """

        # JWT decode options.
        verify_signature = (
            key is not None
        ) or _always_verify_signature  # Do not verify the signature if key is None.
        decode_options = {"verify_signature": verify_signature}

        assert isinstance(token, str)
        try:
            payload = jwt.decode(
                jwt=token,
                key=key,
                options=decode_options,
                algorithms=cls._signing_algorithm,
            )
        except jwt.exceptions.InvalidSignatureError:
            # Raised when token can be decoded but the signature is invalid.
            raise exceptions.TokenInvalidSignatureError
        except jwt.exceptions.ExpiredSignatureError:
            # Raised when token is expired at current time.
            raise exceptions.TokenExpiredError
        except jwt.exceptions.PyJWTError:
            # Raised when there is any error during decoding (
            #   Important notice!
            #   PyJWT raises own error as PyJWTError too,
            #   this means server will throw token invalid error, which is may be caused
            #   by some server side error.
            # )
            raise exceptions.TokenInvalidError

        # Checking token types.
        expected_type = cls._type
        got_type = payload.get("typ", "")
        if got_type != expected_type:
            # Tried to inject another type of token into another type of token.
            raise exceptions.TokenWrongTypeError(
                f"Expected token type to be {expected_type}, but got {got_type}"
            )

        return payload

    def __init__(
        self,
        issuer: str,
        ttl: int | float,
        subject: int,
        payload: dict | None = None,
        *,
        key: str | None = None,
    ):
        """
        Base token constructor.

        :params: Read fields in base class.
        """

        # Assertions for expected types
        assert isinstance(
            payload, dict
        ), "Payload must be a dict (To serialize into JSON)!"
        assert isinstance(issuer, str), "Issuer must be a string (Hostname)"
        assert isinstance(ttl, int | float), "Token TTL must be an number (in seconds)!"
        assert isinstance(
            subject, int
        ), "Token subject must be an integer (ID of the object)"

        # Payload base.
        self.custom_payload = payload if payload is not None else {}

        # Fields.
        self._issuer = issuer
        self._ttl = ttl
        self._subject = subject

        # Optional key.
        self._key = key
