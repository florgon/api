"""
    Permission service, works with scope, permissions.
    OAuth permissions.
    Read more at docs: https://florgon.com/dev/apis/auth
"""
from enum import Enum


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
    phone = "phone"

    # Private.
    admin = "admin"

    # Services.
    messenger = "messenger"
    gatey = "gatey"
    cc = "cc"
    ads = "ads"


def scopes_is_same(a: str, b: str) -> bool:
    """
    Checks that two scopes is same by parsing them.
    """
    return parse_permissions_from_scope(a) == parse_permissions_from_scope(b)


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
        return set(SCOPE_ALL_PERMISSIONS)
    return {
        Permission(permission)
        for permission in scope.split(SCOPE_PERMISSION_SEPARATOR)
        if (permission and permission in SCOPE_ALLOWED_PERMISSIONS)
    }


def permissions_get_ttl(permissions: set[Permission], default_ttl: int) -> int:
    """
    Returns TTL for token, based on given permissions list.
    """
    return 0 if Permission.noexpire in permissions else default_ttl


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
    Permission.phone,
]

# Allowed permission, as string list.
SCOPE_ALLOWED_PERMISSIONS = list(
    map(
        lambda p: p.value,
        SCOPE_ALL_PERMISSIONS,
    )
)
