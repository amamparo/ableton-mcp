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

# Install control surface to Ableton's Remote Scripts directory
install-control-surface:
    #!/usr/bin/env bash
    set -euo pipefail
    TARGET_DIR="$HOME/Music/Ableton/User Library/Remote Scripts/AbletonMCP"
    mkdir -p "$TARGET_DIR"
    cp -r control_surface/AbletonMCP/* "$TARGET_DIR/"
    echo "Control surface installed to $TARGET_DIR"
    echo "Restart Ableton Live and select AbletonMCP in Preferences > Link, Tempo & MIDI"

# Clean build artifacts
clean:
    rm -rf dist/ build/ *.egg-info .pytest_cache .mypy_cache .ruff_cache
    find . -type d -name __pycache__ -exec rm -rf {} +
