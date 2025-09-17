.PHONY: bootstrap lint format typecheck test ingest run up down

bootstrap:
	pip install -e .[dev]
	pre-commit install

lint:
	ruff check src tests

format:
	ruff check --fix src tests
	ruff format src tests

typecheck:
	mypy src

test:
	pytest

ingest:
	python -m src.workers.ingest

run:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

up:
	docker compose -f docker/docker-compose.yml up -d --build

down:
	docker compose -f docker/docker-compose.yml down -v
