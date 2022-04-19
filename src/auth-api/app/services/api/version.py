"""
    Current API version.
    Should it be exposed to config?
    I think developer should change this in CODE, as releated to code changes...
"""

API_VERSION = "1.2.3"

API_CHANGELOG = {
    "versions": {
            "1.0": {
                "1.0": [
                    "Initial release.",
                ],
                "1.0.1": [
                    "Allowed CORS requests."
                ],
                "1.0.2": [
                    "New `/verify` method that returns is given token valid or not and decoded information about token.",
                    "Email notification when new user sign up (Email notification events may be changed without notice here)"
                ],
                "1.0.3": [
                    "Tokens now includes `_user` and `username`"
                ],
                "1.1.3": [
                    "New email confirmation system.",
                    "New methods `/email/confirm`, `email/resend_confirmation`.",
                    "Renamed user state `is_verified` to `is_confirmed`.",
                    "Username from now should contain only lowercase alphabet characters."
                ],
                API_VERSION: [
                    "New route `/oauth/direct`, which is the same as `/signin` but requires `client_id` and `client_secret` field which is may be acquired by route below.",
                    "New route `/oauth/client/new` which is creates new OAuth client.",
                    "New route `/oauth/client/expire` which is regenerates OAuth client secret.",
                    "New route `/oauth/external` which is not implemented yet (Due to current API structure).",
                ]
            }
        }
}