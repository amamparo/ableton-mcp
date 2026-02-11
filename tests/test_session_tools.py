import json

import pytest


@pytest.mark.anyio
async def test_get_session_info(fake_client, mcp_server):
    fake_client.set_response(
        "get_session_info",
        {
            "tempo": 120.0,
            "signature_numerator": 4,
            "signature_denominator": 4,
            "track_count": 3,
            "return_track_count": 2,
        },
    )

    content, _ = await mcp_server.call_tool("get_session_info", {})
    result = json.loads(content[0].text)

    assert result["tempo"] == 120.0
    assert result["track_count"] == 3
    assert fake_client.commands_sent == [("get_session_info", {})]


@pytest.mark.anyio
async def test_get_track_info(fake_client, mcp_server):
    fake_client.set_response(
        "get_track_info",
        {
            "name": "Bass",
            "mute": False,
            "solo": False,
            "volume": 0.85,
            "pan": 0.0,
            "devices": [],
        },
    )

    content, _ = await mcp_server.call_tool("get_track_info", {"track_index": 0})
    result = json.loads(content[0].text)

    assert result["name"] == "Bass"
    assert result["volume"] == 0.85
    assert fake_client.commands_sent == [("get_track_info", {"track_index": 0})]


@pytest.mark.anyio
async def test_connection_error_returns_error_json(mcp_server):
    content, _ = await mcp_server.call_tool("get_session_info", {})
    result = json.loads(content[0].text)
    assert "error" in result
