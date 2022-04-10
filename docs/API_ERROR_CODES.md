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