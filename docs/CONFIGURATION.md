# Configuration.
TODO.

## Configuration fields.
### JWT.
- jwt_secret
- - Secret key for JWT signature.
- jwt_issuer
- - Name of the JWT token issuer, does not change any staff.
- jwt_ttl
- - JWT token time to live after that token is expires.
### CFT.
- cft_secret
- - Secret key for confirmation tokens,
- cft_salt
- - Salt for generating confirmation tokens.
- cft_max_age
- - Max age for confirmation tokens.
### Proxy.
- proxy_url_prefix
- - This prefix will be used for all routes. (For proxies).
- proxy_url_host
- - Proxy host for generating urls.
### Mail.
- mail_from_name
- - This name will be used for all emails (like "Florgon Auth")
- mail_host_server
- - SMTP host server url.
- mail_host_password
- - Password for mail.
- mail_host_username
- - Username for mail.