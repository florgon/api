"""
    Florgon API tokens.

    Provides class interfaces for working with tokens (access / session / etc).
    Provides base class `_token._Token` for implementation of own token type.
    All tokens should be child classes of _Token class.
"""

from . import (
    access_token,
    session_token,

    email_token,
    
    oauth_code,
)