# Florgon API.

[![Unit tests](https://github.com/florgon/api/actions/workflows/unittests.yml/badge.svg)](https://github.com/florgon/api/actions/workflows/unittests.yml)
[![Deploy in production](https://github.com/florgon/api/actions/workflows/deploy.yml/badge.svg)](https://github.com/florgon/api/actions/workflows/deploy.yml) \
[![Linters](https://github.com/florgon/api/actions/workflows/linters.yml/badge.svg)](https://github.com/florgon/api/actions/workflows/linters.yml)
[![CodeQL](https://github.com/florgon/api/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/florgon/api/actions/workflows/codeql-analysis.yml)

### Description.

API server for Florgon services (Florgon API).

### Features.

- Authentication (OAuth, Permissions, 2FA, Sessions)
- Accounts (Public profile, Private accounts).
- Administrators stuff.
- Email verification system.
- VIP system (with promocodes).
- Upload system (With upload server).
- Blog system.

### See in action.

API deployed and used in production [here](https://api.florgon.space/) (API endpoint).

### Contributing.

(You may install `requirements-dev.txt`)
There is auto check for `black` formatter, and `pylint` linter for warnings.
Also your request should pass unit-tests (and overall smoke test).
Before sending PR, you should do `black` formatting, and `pylint` check!

### Technologies.

- Python (FastAPI, SQLAlchemy).
- PostgreSQL (with pgBouncer)
- Redis (Handle requests limit)
- Docker (with Docker-Compose),
- Uvicorn (with Gunicorn)
- PyTest (GitHub workflows)

# Docs.

### Running | Deploy.

How to run: [`/docs/deployment/HOW_TO_RUN.md`](/docs/deployment/HOW_TO_RUN.md) \
How to configure: [`/docs/deployment/CONFIGURATION.md`](/docs/deployment/CONFIGURATION.md)

### API.

API methods: [`/docs/api/API_METHODS.md`](/docs/api/API_METHODS.md) \
API response structure: [`/docs/api/API_RESPONSE.md`](/docs/api/API_RESPONSE.md) \
API error codes: [`/docs/api/API_ERROR_CODES.md`](/docs/api/API_ERROR_CODES.md)

### Other.

Integrating Florgon OAuth: [`/docs/OAUTH.md`](/docs/OAUTH.md)
