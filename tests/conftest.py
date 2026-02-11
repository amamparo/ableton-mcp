from __future__ import annotations

from typing import Any

import pytest
from injector import Injector, Module, provider, singleton

from ableton_mcp.client import AbletonClient
from ableton_mcp.server import create_server


class FakeAbletonClient(AbletonClient):
    """In-memory fake that returns canned responses keyed by command type."""

    def __init__(self) -> None:
        self.commands_sent: list[tuple[str, dict[str, Any]]] = []
        self._responses: dict[str, dict[str, Any]] = {}

    def set_response(self, command_type: str, result: dict[str, Any]) -> None:
        self._responses[command_type] = result

    def send_command(
        self, command_type: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self.commands_sent.append((command_type, params or {}))
        if command_type not in self._responses:
            raise RuntimeError(f"No fake response configured for '{command_type}'")
        return self._responses[command_type]


class FakeAbletonModule(Module):
    def __init__(self, fake_client: FakeAbletonClient) -> None:
        self._fake_client = fake_client

    @singleton
    @provider
    def provide_ableton_client(self) -> AbletonClient:
        return self._fake_client


@pytest.fixture
def fake_client():
    return FakeAbletonClient()


@pytest.fixture
def mcp_server(fake_client):
    injector = Injector([FakeAbletonModule(fake_client)])
    return create_server(injector)
