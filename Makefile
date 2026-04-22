.PHONY: dev infra-up infra-down migrate upgrade

dev:
	uv run uvicorn app.main:app --reload --port 8000

infra-up:
	docker compose up -d

infra-down:
	docker compose down -v

migrate:
	uv run alembic revision --autogenerate -m "$(m)"

upgrade:
	uv run alembic upgrade head