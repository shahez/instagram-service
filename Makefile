.PHONY: help install setup start stop test clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install Python dependencies"
	@echo "  make setup      - Initialize LocalStack resources"
	@echo "  make start      - Start LocalStack services"
	@echo "  make stop       - Stop LocalStack services"
	@echo "  make test       - Run all tests"
	@echo "  make test-cov   - Run tests with coverage report"
	@echo "  make clean      - Clean up generated files"
	@echo "  make reset      - Stop services and clean data"

install:
	pip install -r requirements.txt

setup:
	@echo "Waiting for LocalStack to be ready..."
	@sleep 5
	python scripts/setup.py

start:
	docker-compose up -d
	@echo "LocalStack is starting..."
	@sleep 5
	@make setup

stop:
	docker-compose down

test:
	pytest -v

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term-missing
	@echo "\nCoverage report generated in htmlcov/index.html"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

reset:
	docker-compose down -v
	@make clean
	@echo "All services stopped and data cleaned"
