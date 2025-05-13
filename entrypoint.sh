#!/bin/bash
# Normalize line endings in scripts, Python files, and Alembic migrations
find /app -type f \( -name '*.sh' -o -name '*.py' -o -name '*.ini' -o -path '/app/alembic/*' \) \
  -exec sed -i 's/\r$//' {} +
set -e

echo "▶ Running migrations..."
alembic upgrade head

if [ "$RUN_TESTS" = "1" ]; then # Pro automatické spouštění testů
  echo "▶ Running tests..."
  pytest -q
  exit $?
fi

exec "$@"