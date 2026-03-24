.PHONY: install dev test lint format clean run-api run-bot

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache htmlcov .mypy_cache

run-api:
	uvicorn src.api.main:app --reload --port 8000

run-bot:
	python src/core/bot/thdora_bot.py

run-demo:
	python src/core/demo.py
