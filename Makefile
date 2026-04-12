.PHONY: install dev test lint format clean run-api run-bot \
        docker-build docker-up docker-down docker-logs docker-db docker-shell-api

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html

test-bot:
	pytest tests/unit/bot/ tests/bot/ -v

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache htmlcov .mypy_cache

# ─ LOCAL ────────────────────────────────────────────────────────────
run-api:
	uvicorn src.api.main:app --reload --port 8000

run-bot:
	python -m src.bot.main

run-demo:
	python src/core/demo.py

# ─ DOCKER ───────────────────────────────────────────────────────────
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-logs-api:
	docker compose logs -f api

docker-logs-bot:
	docker compose logs -f bot

docker-db:
	docker compose exec api sqlite3 /app/data/thdora.db

docker-shell-api:
	docker compose exec api sh

docker-restart:
	docker compose restart

docker-rebuild:
	docker compose down && docker compose build --no-cache && docker compose up -d
