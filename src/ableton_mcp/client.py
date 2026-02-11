from __future__ import annotations

import json
import socket
from abc import ABC, abstractmethod
from typing import Any


class AbletonClient(ABC):
    """Abstract interface for communicating with Ableton Live."""

    @abstractmethod
    def send_command(
        self, command_type: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Send a command and return the result dict.

        Raises RuntimeError on connection or protocol errors.
        """
        ...


class SocketAbletonClient(AbletonClient):
    """Connects to the AbletonMCP control surface over TCP/JSON."""

    def __init__(self, host: str = "localhost", port: int = 9877) -> None:
        self._host = host
        self._port = port
        self._sock: socket.socket | None = None

    def connect(self) -> None:
        if self._sock is not None:
            return
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._host, self._port))

    def disconnect(self) -> None:
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    def send_command(
        self, command_type: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if self._sock is None:
            self.connect()
        assert self._sock is not None

        payload = json.dumps({"type": command_type, "params": params or {}}).encode(
            "utf-8"
        )
        self._sock.sendall(payload)

        try:
            response_data = self._receive_full_response()
        except (ConnectionError, BrokenPipeError, OSError):
            self._sock = None
            raise RuntimeError(
                "Lost connection to Ableton. Is the control surface running?"
            )

        response = json.loads(response_data.decode("utf-8"))

        if response.get("status") == "error":
            raise RuntimeError(response.get("message", "Unknown error from Ableton"))

        return response.get("result", {})

    def _receive_full_response(
        self, buffer_size: int = 8192, timeout: float = 15.0
    ) -> bytes:
        assert self._sock is not None
        self._sock.settimeout(timeout)
        chunks: list[bytes] = []
        while True:
            chunk = self._sock.recv(buffer_size)
            if not chunk:
                break
            chunks.append(chunk)
            data = b"".join(chunks)
            try:
                json.loads(data.decode("utf-8"))
                return data
            except json.JSONDecodeError:
                continue
        if chunks:
            return b"".join(chunks)
        raise RuntimeError("No data received from Ableton")
