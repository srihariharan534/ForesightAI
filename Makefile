.PHONY: setup lint format test build run clean

setup:
	python -m venv venv
	./venv/Scripts/python -m pip install --upgrade pip
	./venv/Scripts/python -m pip install -r requirements.txt
	./venv/Scripts/pre-commit install

lint:
	ruff check .
	mypy .

format:
	black .
	isort .

test:
	pytest backend/tests/ --cov=backend

build:
	docker-compose build

run:
	docker-compose up

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
