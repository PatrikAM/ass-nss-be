#!/bin/bash
set -e

echo "▶ Running migrations..."
alembic upgrade head

if [ "$RUN_TESTS" = "1" ]; then
  echo "▶ Running tests..."
  pytest -q
  exit $?
fi

exec "$@"