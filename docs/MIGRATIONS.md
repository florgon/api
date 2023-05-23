# Database migrations

Florgon API uses **Alembic** as migrations provider. For more detailed documentation see https://alembic.sqlalchemy.org.

All commands should be executed in server docker compose service. You can run it interactively in container:

```bash
docker compose exec server sh
```

## Create migration

Update one of database models, then run:

```bash
alembic revision -m "<Your message about changes in DB>"
```

## Upgrade

To latest migration:

```bash
alembic upgrade head
```

Relatively to current state:

```bash
alembic upgrade +2
```

```bash
alembic downgrade -1
```

## History

Show current state:

```bash
alembic current
```

Show history

```bash
alembic history --verbose
```
