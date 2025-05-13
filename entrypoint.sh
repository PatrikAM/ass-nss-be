#!/bin/bash
# Normalize line endings to Unix format for Windows-mounted files
sed -i 's/\r$//' "$0"
set -e

echo "▶ Running migrations..."
alembic upgrade head

if [ "$RUN_TESTS" = "1" ]; then # Pro automatické spouštění testů
  echo "▶ Running tests..."
  pytest -q
  exit $?
fi

exec "$@"