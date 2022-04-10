# Configuration.
All settings changed under `/src/auth-api/.env` file, that is being processed with `pydantic` as `.env` settings.

## Configuration fields.
- jwt_secret
- - Secret key for JWT signature.
- jwt_issuer
- - Name of the JWT token issuer, does not change any staff.
- jwt_ttl
- - JWT token time to live after that token is expires.