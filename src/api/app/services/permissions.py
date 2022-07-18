from enum import Enum


class Permission(Enum):
    # Other.
    noexpire = "noexpire"

    # Profile.
    edit = "edit"
    sessions = "sessions"
    oauth_clients = "oauth_clients"
    email = "email"

    # Private.
    admin = "admin"

    # Services.
    konkursnik="konkursnik"
    gatey = "gatey"
    notes = "notes"
    habits = "habits"
    ads = "ads"
    cc = "cc"



Permissions = list[Permission]  # Type hint (alias).


def normalize_scope(scope: str) -> str:
    return SCOPE_PERMISSION_SEPARATOR.join(
        [permission.value for permission in parse_permissions_from_scope(scope)]
    )


def permissions_get_ttl(permissions: Permissions, default_ttl: int) -> int:
    if Permission.noexpire in permissions:
        return 0
    return default_ttl


def parse_permissions_from_scope(scope: str) -> Permissions:
    assert isinstance(scope, str)
    if SCOPE_PERMISSION_GRANT_ALL_TAG in scope:
        return SCOPE_ALL_PERMISSIONS
    return list(
        set(
            [
                Permission(permission)
                for permission in scope.split(SCOPE_PERMISSION_SEPARATOR)
                if (permission and permission in SCOPE_ALLOWED_PERMISSIONS)
            ]
        )
    )


SCOPE_PERMISSION_GRANT_ALL_TAG = "*"
SCOPE_PERMISSION_SEPARATOR = ","
SCOPE_ALL_PERMISSIONS = [
    Permission.oauth_clients,
    Permission.email,
    Permission.noexpire,
    Permission.admin,
    Permission.edit,
    Permission.sessions,
    Permission.gatey,
    Permission.notes,
    Permission.habits,
    Permission.ads,
    Permission.cc,
    Permission.konkursnik,
]
SCOPE_ALLOWED_PERMISSIONS = list(
    map(
        lambda p: p.value,
        SCOPE_ALL_PERMISSIONS,
    )
)
