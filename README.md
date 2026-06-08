# Doação

Aplicação destinada a gestão de doações. Todo domingo o grupo monta kits de
alimentação; durante a semana os voluntários registram o que vão levar.

## Setup

```bash
uv sync
cp .env.example .env  # edite SECRET_KEY e DEBUG=on
uv run python manage.py migrate
uv run python manage.py seed
uv run python manage.py runserver
```

Tailwind (watcher): `docker compose up`

Testes: `uv run pytest`