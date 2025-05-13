# How to run

`docker compose up --build`

# Get to documentation

`http://localhost:8000/docs`

# How to work with alembic (migration tool)

## How to create new migration
`alembic revision -m "Create measurement and config tables"`

## How to apply migrations
`alembic upgrade head`

## How to revert migrations
`alembic downgrade head`

## How to show current migration
`alembic current`

## How to run tests

### Unit (mock) tests

Run the mock-based unit tests (skipping integration tests):
```bash
pytest test_main.py
```

### Integration tests

Run the full test suite including integration tests by setting the RUN_TESTS environment variable:

```bash
# Locally
RUN_TESTS=1 pytest test_main.py

# With Docker Compose
docker-compose run --rm -e RUN_TESTS=1 fastapi
```
