.PHONY: test test-unit test-api test-integration test-cov test-all

test: ## Run all tests
	uv run python -m pytest tests/ -v

test-unit: ## Run unit tests only
	uv run python -m pytest tests/unit/ -v

test-api: ## Run API acceptance tests
	uv run python -m pytest tests/test_auth.py -v

test-integration: ## Run integration tests
	uv run python -m pytest tests/integration/ -v

test-cov: ## Run all tests with coverage report
	uv run python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=xml

test-all: test-cov ## Run everything (alias for test-cov)
