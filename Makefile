# Developer convenience targets. Each maps to the underlying tool so the
# commands work identically in CI and on a developer machine.

.PHONY: help install test lint format typecheck check run clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

install: ## Install the package with development dependencies
	python -m pip install -e ".[dev]"

test: ## Run the test suite with coverage
	pytest --cov --cov-report=term-missing

lint: ## Lint the code
	ruff check .

format: ## Auto-format the code
	ruff format .

typecheck: ## Run static type checking
	mypy

check: lint typecheck test ## Run every quality gate (lint + types + tests)

run: ## Run the tool against the sample log (example from the brief)
	python -m most_active_cookie -f cookie_log.csv -d 2018-12-09

clean: ## Remove caches and build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage \
		build dist src/*.egg-info
