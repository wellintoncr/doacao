#!/bin/bash
set -e

echo "Starting deploy..."

git restore .

git pull
uv sync --frozen
uv run python manage.py migrate
uv run python manage.py collectstatic --no-input

echo "Deploy complete."
