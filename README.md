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
