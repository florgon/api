# API error codes.

### Auth field taken.
- 0 [AUTH_USERNAME_TAKEN]
- - Given username is already taken.
- 1 [AUTH_EMAIL_TAKEN]
- - Given email is already taken.

### Auth token.
- 10 [AUTH_INVALID_TOKEN]
- - Token has invalid format or has invalid signature.
- 11 [AUTH_EXPIRED_TOKEN]
- - Token has been expired, please get net.

# Auth other.
- 20 [AUTH_INVALID_CREDENTIALS]
- - You trying to login with invalid password or login (username || email).
- 21 [AUTH_REQUIRED]
- - You should send `token` param or `Authorization` header in order to process to given method.

## Auth field invalid.
- 30 [AUTH_EMAIL_INVALID]
- - Email should have valid format (And maybe valid DNS).
- 31 [AUTH_PASSWORD_INVALID]
- - Password should be longer than 5 and shorten than 64.
- 32 [AUTH_USERNAME_INVALID]
- - Password should be longer than 4 and shorten than 16.

# API.
- 40 [API_INVALID_REQUEST]
- - One or more of your params has been not found inside request, please read more about requested method and it params.
- 41 [API_NOT_IMPLEMENTED]
- - Method that you requested is not implemented yet.
- 42 [API_INTERNAL_SERVER_ERROR]
- - Some internal error at server side. Try wait some time, or contact support.
- 43 [API_METHOD_NOT_FOUND]
- - Method (URL) that you requested does not exists.


# Email confirmation.
- 50 [EMAIL_CONFIRMATION_TOKEN_INVALID]
- - Your confirmation token is invalid, maybe it expired?
- 51 [EMAIL_CONFIRMATION_USER_NOT_FOUND]
- - Confirmation token holds email, that was not found, do you update your email?
- 52 [EMAIL_CONFIRMATION_ALREADY_CONFIRMED]
- - Your email is already confirmed and not required to be confirmed.

# OAUTH.
- 60 [OAUTH_CLIENT_NOT_FOUND]
- - You are trying to get client that does not exists.
- 61 [OAUTH_CLIENT_FORBIDDEN]
- - You are not owner of requested client.
- 61 [OAUTH_CLIENT_REDIRECT_URI_MISMATCH]
- - redirect_uri not same.
- 62 [OAUTH_CLIENT_ID_MISMATCH]
- - client_id not same.
- 63 [OAUTH_CLIENT_SECRET_MISMATCH]
- - Client secret not valid.

# User.
- 100 [USER_DEACTIVATED]
- - You has been deactivated, and dissalowed to do this action. Please contact support (Mostly due to ban reason)