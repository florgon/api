"""
    Florgon API token exceptions.
"""


class TokenWrongTypeError(Exception):
    """
    Token injected with wrong type.
    (Tried to decode token with type access for example, in session token).
    """


class TokenExpiredError(Exception):
    """
    Token expired.
    (Token `exp` field less than current time)
    """


class TokenInvalidError(Exception):
    """
    Token has invalid format or there is unexpected error during token decoding.
    """


class TokenInvalidSignatureError(Exception):
    """
    Token has invalid signature.
    (Maybe not raised due to token decoding being explicitly set key to None
    for decoding without signature verification).
    """
