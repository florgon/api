from enum import Enum


class Permission(Enum):
    oauth_clients = "oauth_clients"
    email = "email"
    noexpire = "noexpire"


def normalize_scope(scope: str) -> str:
    return SCOPE_PERMISSION_SEPARATOR.join([permission.value for permission in parse_permissions_from_scope(scope)])


def parse_permissions_from_scope(scope: str) -> set[Permission]:
    return set([
        Permission[permission] for permission in 
        scope.split(SCOPE_PERMISSION_SEPARATOR)
        if (permission and permission in SCOPE_ALLOWED_PERMISSIONS and permission)
    ])


SCOPE_PERMISSION_SEPARATOR = ","
SCOPE_ALLOWED_PERMISSIONS = [permission.value for permission in [
    Permission.oauth_clients,
    Permission.email,
    Permission.noexpire
]]