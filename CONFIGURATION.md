# Florgon API configuration.

API provides some amount of sections for configuration.
Currently, all settings are inside environment variables (look more into `*.env` / `*.env.example` files)

### Mail

All variables prefixed with `MAIL_`. For obtaining server information please read documentation from your mail provider.

| Variable        | Type                | Description                                                                  |
| --------------- | ------------------- | ---------------------------------------------------------------------------- |
| SUPRESS_SEND    | bool, true or false | Will not send any real mail (always enabled when in development environment) |
| SERVER          | bool                | Hostname of the mail server                                                  |
| USERNAME        | str                 | Username for mail server authorization                                       |
| PASSWORD        | str                 | Password for mail server authorization                                       |
| FROM_NAME       | str or void, void   | Used for `mail-from` with all mails                                          |
| FROM_MAIL       | str                 | Mail to use for sending mail                                                 |
| PORT            | int or void, void   | Mail host provider port (will guess from tls/ssl if no)                      |
| STARTTLS        | bool, false         | STARTTLS for host provider                                                   |
| SSL_TLS         | bool, true          | SSL/TLS for host provider                                                    |
| USE_CREDENTIALS | bool, true          | Undocumented                                                                 |
| VALIDATE_CERTS  | bool, true          | Undocumented                                                                 |
| TIMEOUT         | int, 60             | Undocumented                                                                 |

### Database

All variables prefixed with `POSTGRES_DB_`.
Please, change default configuration of database (not leaving default database user fields).

| Variable                  | Type           | Description            |
| ------------------------- | -------------- | ---------------------- |
| NAME                      | str, database  | Database name          |
| USER                      | str, postgres  | Database username      |
| PASSWORD                  | str, postgres  | Database user password |
| HOST                      | str, localhost | Database hostname      |
| PORT                      | int, 5432      | Database port          |
| ORM_ECHO_STATEMENTS       | bool, True     | Undocumented           |
| ORM_ECHO_STATEMENTS_DEBUG | bool, False    | Undocumented           |
| ORM_CREATE_ALL            | bool, True     | Undocumented           |
| ORM_MAX_OVERFLOW          | int, 0         | Undocumented           |
| ORM_POLL_PRE_PING         | bool, True     | Undocumented           |
| ORM_POOL_RECYCLE          | int, 3600      | Undocumented           |
| ORM_POOL_TIMEOUT          | int, 10        | Undocumented           |
| ORM_POLL_SIZE             | int, 20        | Undocumented           |

### Logging

All variables prefixed with `LOGGING_`.

| Variable | Type                | Description      |
| -------- | ------------------- | ---------------- |
| NAME     | str, gunicorn.error | Core logger name |

### Gatey

All variables prefixed with `GATEY_`.
If there is misconfiguration or no configuration, Gatey client will not boot.

| Variable              | Type              | Description                        |
| --------------------- | ----------------- | ---------------------------------- |
| project_id            | int or void, void | Project ID                         |
| client_secret         | str or void, void | Client Secret                      |
| server_secret         | str or void, void | Server Secret                      |
| send_setup_event      | bool, true        | Will send setup event when started |
| capture_requests_info | bool, false       | Will capture requests info         |

### OpenAPI

All variables prefixed with `OPENAPI_`.

| Variable      | Type                 | Description                         |
| ------------- | -------------------- | ----------------------------------- |
| expose_public | bool, false          | Will expose openapi, ReDoc, Swagger |
| url           | str, "/openapi.json" | URL to the OpenAPI                  |
| docs_url      | str, "/docs"         | URL to the Swagger docs             |
| redoc_url     | str, "/redoc/"       | URL to the redoc                    |
| prefix        | str, ""              | OpenAPI prefix                      |

### Misc.

No documentation for other configuration settings for now.
