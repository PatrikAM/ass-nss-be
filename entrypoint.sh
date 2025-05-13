#!/bin/bash
# Convert this script and Alembic migrations to LF line endings
if command -v dos2unix >/dev/null 2>&1; then
  dos2unix "${BASH_SOURCE[0]}"
  find /app/alembic -type f -exec dos2unix {} +
fi

set -e

echo "▶ Running migrations..."
alembic upgrade head

if [ "$RUN_TESTS" = "1" ]; then

  echo "▶ Running tests..."
  pytest -q
  exit $?
fi

exec "$@"
