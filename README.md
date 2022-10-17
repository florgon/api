# Florgon API.

[![Deploy in production](https://github.com/florgon/api/actions/workflows/deploy.yml/badge.svg)](https://github.com/florgon/api/actions/workflows/deploy.yml) \
[![Tests](https://github.com/florgon/api/actions/workflows/tests.yml/badge.svg)](https://github.com/florgon/api/actions/workflows/tests.yml)
[![CodeQL](https://github.com/florgon/api/actions/workflows/codeql.yml/badge.svg)](https://github.com/florgon/api/actions/workflows/codeql.yml) \
[![Linters](https://github.com/florgon/api/actions/workflows/linters.yml/badge.svg)](https://github.com/florgon/api/actions/workflows/linters.yml)
[![Formatters](https://github.com/florgon/api/actions/workflows/formatters.yml/badge.svg)](https://github.com/florgon/api/actions/workflows/formatters.yml) \
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen?style=flat)](https://github.com/PyCQA/pylint) \
<a href="https://github.com/florgon/api/blob/main/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>

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

# Tested on...

Docker engine: v20.* \
Docker compose: v2.*
