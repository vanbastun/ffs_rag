.PHONY: bootstrap lint format typecheck test ingest run up down eval

bootstrap:
\tpip install -e .[dev]
\tpre-commit install

lint:
\truff check src tests

format:
\truff check --fix src tests
\tblack src tests

typecheck:
\tmypy src

test:
\tpytest

ingest:
\tpython -m src.workers.ingest

run:
\tuvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

up:
\tdocker compose -f docker/docker-compose.yml up -d --build

down:
\tdocker compose -f docker/docker-compose.yml down -v

eval:
\tpython -m src.rag_core.eval.rag_eval