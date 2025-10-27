.PHONY: help install dev-install run test lint format typecheck clean docker-build docker-run docker-stop docker-clean all

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

dev-install: ## Install development dependencies
	pip install -e ".[dev]"

run: ## Run the application locally with uvicorn
	uvicorn app.main:app --reload --port 8080 --log-level info

serve: ## Run the application in production mode
	uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4

test: ## Run tests with coverage
	pytest --maxfail=1 --cov=app -v

test-fast: ## Run tests without coverage (faster)
	pytest --maxfail=1 -x

test-verbose: ## Run tests with verbose output
	pytest --maxfail=1 --cov=app -vv

lint: ## Run linters (ruff)
	ruff check .

lint-fix: ## Run linters with auto-fix
	ruff check --fix .

format: ## Format code with black
	black .

format-check: ## Check code formatting without making changes
	black --check .

typecheck: ## Run type checking with mypy
	mypy app

check: lint format-check typecheck ## Run all checks (lint, format, typecheck)

fix: lint-fix format ## Fix all auto-fixable issues

clean: ## Clean up generated files
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete

docker-build: ## Build Docker image
	docker build -t mits-validator-api:latest .

docker-run: ## Run Docker container
	docker-compose up -d

docker-stop: ## Stop Docker container
	docker-compose down

docker-clean: ## Stop and remove Docker containers, networks, and volumes
	docker-compose down -v
	docker rmi mits-validator-api:latest || true

docker-logs: ## View Docker container logs
	docker-compose logs -f

docker-shell: ## Open shell in Docker container
	docker-compose exec api /bin/bash

all: clean install check test ## Run complete build pipeline

ci: check test ## Run CI pipeline locally

