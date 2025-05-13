#!/bin/bash
# Convert CRLF → LF for this script when mounted from Windows
dos2unix "$0" >/dev/null 2>&1 || true

set -e

echo "▶ Running migrations..."
alembic upgrade head

if [ "$RUN_TESTS" = "1" ]; then
  echo "▶ Running tests..."
  pytest -q
  exit $?
fi

exec "$@"