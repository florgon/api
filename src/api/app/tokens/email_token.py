"""
    Florgon API email token implementation.
"""


from ._token import _Token


class EmailToken(_Token):
    """
    Email token JWT implementation.

    Used to confirm email address.
    """

    _type = "email"
