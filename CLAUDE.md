# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run via `just` (see `justfile`):

- `just check` — run lint + tests (default)
- `just lint` — Black formatting check + Ruff linting
- `just test` — run pytest
- `just fmt` — auto-format with Black
- `just install` — install Poetry dependencies
- `poetry run pytest tests/test_file.py::test_name` — run a single test

## Architecture

This is an MCP (Model Context Protocol) server for Ableton Live, built with FastMCP.

**Key files:**
- `src/ableton_mcp/server.py` — MCP server factory and tool definitions
- `src/ableton_mcp/__main__.py` — entrypoint (`ableton-mcp` CLI command)

**Dependency injection:** Uses the `injector` library. Services are bound in `AbletonModule` and resolved via `injector.get()` inside tool handlers. The `create_server()` factory accepts an optional `Injector` to allow swapping implementations in tests.

**Testing pattern:** Tests use `@pytest.mark.anyio` for async. Call tools directly via `mcp.call_tool(name, args)` which returns `(content_list, raw_result)`. Pass a custom `Injector` to `create_server()` to substitute fakes.

## Code Style

- Python 3.12+, PEP 8, Black with 88-char line length
- Ruff for linting (rules: E, F, I, W)
