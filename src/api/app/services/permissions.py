"""
    Permission service, works with scope, permissions.
    OAuth permissions.
    Read more at docs: https://florgon.space/dev/apis/auth
"""
from enum import Enum
from typing import Iterable


class Permission(Enum):
    """
    Permissions scope string enumeration.
    """

    # Other.
    noexpire = "noexpire"

    # Profile.
    edit = "edit"
    sessions = "sessions"
    oauth_clients = "oauth_clients"
    email = "email"
    security = "security"

    # Private.
    admin = "admin"

    # Services.
    messenger = "messenger"
    gatey = "gatey"
    cc = "cc"
    ads = "ads"


def __scope_to_permission_code(scope: str):
    """
    TBD. Not documented and not used.
    """
    if not isinstance(scope, str):
        raise TypeError("Scope must be a string!")
    permissions = parse_permissions_from_scope(scope)
    return "".join(
        [
            "1" if permission in permissions else "0"
            for permission in __CODE_PERMISSIONS_ORDER
        ]
    )


def __parse_permissions_from_code(code: str) -> set[Permission]:
    """
    TBD. Not documented and not used.
    """
    if not isinstance(code, str):
        raise TypeError("Code must be a string!")
    permissions = []
    for code_bit_index, code_bit in enumerate(code):
        if code_bit != "1":
            continue
        code_bit_permission = __CODE_PERMISSIONS_ORDER[code_bit_index]
        permissions.append(code_bit_permission)
    return set(permissions)


def normalize_scope(scope: str) -> str:
    """
    Returns normalized scope from scope, means there is no repeated scopes and maybe some unused symbols.
    """
    if not isinstance(scope, str):
        raise TypeError("Scope must be a string!")
    return SCOPE_PERMISSION_SEPARATOR.join(
        [permission.value for permission in parse_permissions_from_scope(scope)]
    )


def parse_permissions_from_scope(scope: str) -> set[Permission]:
    """
    Returns list of permissions from scope, by parsing it.
    """
    if not isinstance(scope, str):
        raise TypeError("Scope must be a string!")
    if SCOPE_PERMISSION_GRANT_ALL_TAG in scope:
        return SCOPE_ALL_PERMISSIONS
    return {
        Permission(permission)
        for permission in scope.split(SCOPE_PERMISSION_SEPARATOR)
        if (permission and permission in SCOPE_ALLOWED_PERMISSIONS)
    }


def permissions_get_ttl(permissions: set[Permission], default_ttl: int) -> int:
    """
    Returns TTL for token, based on given permissions list.
    """
    if Permission.noexpire in permissions:
        return 0
    return default_ttl


# TBD. Not documented and not used.
__CODE_PERMISSIONS_ORDER = [
    Permission.email,
    Permission.edit,
    Permission.sessions,
    Permission.noexpire,
    Permission.oauth_clients,
    Permission.admin,
    Permission.security,
    Permission.gatey,
    Permission.ads,
    Permission.messenger,
    Permission.cc,
]

# String tags, for separator and modificator that gives all permissions.
SCOPE_PERMISSION_GRANT_ALL_TAG = "*"
SCOPE_PERMISSION_SEPARATOR = ","

# List of all permissions.
SCOPE_ALL_PERMISSIONS = [
    Permission.oauth_clients,
    Permission.email,
    Permission.noexpire,
    Permission.admin,
    Permission.edit,
    Permission.security,
    Permission.sessions,
    Permission.gatey,
    Permission.ads,
    Permission.messenger,
    Permission.cc,
]

# Allowed permission, as string list.
SCOPE_ALLOWED_PERMISSIONS = list(
    map(
        lambda p: p.value,
        SCOPE_ALL_PERMISSIONS,
    )
)
