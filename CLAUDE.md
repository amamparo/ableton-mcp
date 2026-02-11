# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run via `just` (see `justfile`):

- `just check` — run lint + tests (default)
- `just lint` — Black formatting check + Ruff linting
- `just test` — run pytest
- `just fmt` — auto-format with Black
- `just install` — install Poetry dependencies
- `just install-control-surface` — copy control surface to Ableton's Remote Scripts
- `poetry run pytest tests/test_file.py::test_name` — run a single test

## Architecture

This is an MCP (Model Context Protocol) server for Ableton Live, built with FastMCP.

**Two components:**
- **MCP Server** (`src/ableton_mcp/`) — FastMCP server that exposes tools to AI agents
- **Control Surface** (`control_surface/AbletonMCP/`) — Python script running inside Ableton Live that exposes the Live Object Model over TCP (port 9877, JSON protocol)

**Key files:**
- `src/ableton_mcp/server.py` — MCP server factory and tool definitions
- `src/ableton_mcp/client.py` — `AbletonClient` ABC and `SocketAbletonClient` (TCP/JSON)
- `src/ableton_mcp/__main__.py` — entrypoint (`ableton-mcp` CLI command)
- `control_surface/AbletonMCP/__init__.py` — Ableton control surface (socket server + LOM handlers)

**Dependency injection:** Uses the `injector` library. `AbletonClient` is bound in `AbletonModule` and resolved via `injector.get()` inside tool handlers. The `create_server()` factory accepts an optional `Injector` to allow swapping implementations in tests.

**Testing pattern:** Tests use `@pytest.mark.anyio` for async. Call tools directly via `mcp.call_tool(name, args)` which returns `(content_list, raw_result)`. Pass a custom `Injector` to `create_server()` with `FakeAbletonClient` (see `tests/conftest.py`).

**Socket protocol:** Request: `{"type": "command_name", "params": {...}}` → Response: `{"status": "success|error", "result": {...}, "message": "..."}`. The control surface runs a TCP server; the MCP server connects as a client.

## Code Style

- Python 3.12+, PEP 8, Black with 88-char line length
- Ruff for linting (rules: E, F, I, W)
- Control surface script must be Python 2/3 compatible (no f-strings) for Ableton Live 10+ support
