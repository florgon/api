class ApiAuthRequired(Exception):
    pass

class ApiAuthInvalidToken(Exception):
    pass

class ApiAuthInsufficientPermissions(Exception):
    pass