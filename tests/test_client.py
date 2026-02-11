import json
from unittest.mock import MagicMock, patch

import pytest

from ableton_mcp.client import SocketAbletonClient


class TestSocketAbletonClient:
    def test_send_command_encodes_json(self):
        client = SocketAbletonClient()
        mock_sock = MagicMock()
        mock_sock.recv.return_value = json.dumps(
            {"status": "success", "result": {"tempo": 120.0}}
        ).encode("utf-8")
        client._sock = mock_sock

        result = client.send_command("get_session_info")

        sent_data = mock_sock.sendall.call_args[0][0]
        sent_json = json.loads(sent_data.decode("utf-8"))
        assert sent_json == {"type": "get_session_info", "params": {}}
        assert result == {"tempo": 120.0}

    def test_send_command_with_params(self):
        client = SocketAbletonClient()
        mock_sock = MagicMock()
        mock_sock.recv.return_value = json.dumps(
            {"status": "success", "result": {"name": "Bass"}}
        ).encode("utf-8")
        client._sock = mock_sock

        result = client.send_command(
            "set_track_name", {"track_index": 0, "name": "Bass"}
        )

        sent_data = mock_sock.sendall.call_args[0][0]
        sent_json = json.loads(sent_data.decode("utf-8"))
        assert sent_json == {
            "type": "set_track_name",
            "params": {"track_index": 0, "name": "Bass"},
        }
        assert result == {"name": "Bass"}

    def test_send_command_raises_on_error_status(self):
        client = SocketAbletonClient()
        mock_sock = MagicMock()
        mock_sock.recv.return_value = json.dumps(
            {"status": "error", "message": "Track index out of range"}
        ).encode("utf-8")
        client._sock = mock_sock

        with pytest.raises(RuntimeError, match="Track index out of range"):
            client.send_command("get_track_info", {"track_index": 99})

    def test_disconnect_closes_socket(self):
        client = SocketAbletonClient()
        mock_sock = MagicMock()
        client._sock = mock_sock

        client.disconnect()

        mock_sock.close.assert_called_once()
        assert client._sock is None

    def test_disconnect_noop_when_not_connected(self):
        client = SocketAbletonClient()
        client.disconnect()  # should not raise

    @patch("ableton_mcp.client.socket.socket")
    def test_connect_creates_socket(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock

        client = SocketAbletonClient(host="127.0.0.1", port=1234)
        client.connect()

        mock_sock.connect.assert_called_once_with(("127.0.0.1", 1234))

    @patch("ableton_mcp.client.socket.socket")
    def test_connect_is_idempotent(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock

        client = SocketAbletonClient()
        client.connect()
        client.connect()

        assert mock_socket_cls.call_count == 1
