# Default recipe
default: check

# Install dependencies
install:
    poetry install

# Run all checks (lint + test)
check: lint test

# Format code with Black
fmt:
    poetry run black src/ tests/

# Lint code
lint:
    poetry run black --check src/ tests/
    poetry run ruff check src/ tests/

# Run tests
test:
    poetry run pytest

# Clean build artifacts
clean:
    rm -rf dist/ build/ *.egg-info .pytest_cache .mypy_cache .ruff_cache
    find . -type d -name __pycache__ -exec rm -rf {} +
