.PHONY: install-dev lint format format-check typecheck test test-integration coverage check-docs check clean

UV ?= uv

install-dev:
	$(UV) sync --all-extras --dev

lint:
	$(UV) run ruff check src tests

format:
	$(UV) run ruff format src tests

format-check:
	$(UV) run ruff format --check src tests

typecheck:
	$(UV) run mypy src

test:
	$(UV) run pytest tests/ -m "not integration"

test-integration:
	TRUSTLINE_RUN_INTEGRATION=1 $(UV) run pytest tests/ -m integration

coverage:
	$(UV) run pytest tests/ -m "not integration" --cov=trustline --cov-report=term-missing --cov-fail-under=85

check-docs:
	./scripts/check-docs-publishing.sh

check: check-docs format-check lint typecheck coverage

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov dist build
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
