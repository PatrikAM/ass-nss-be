FROM python:3.11-slim

RUN apt-get update && apt-get install -y bash dos2unix && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN find . -type f -exec dos2unix {} +

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]

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