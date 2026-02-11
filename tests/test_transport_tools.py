import json

import pytest


@pytest.mark.anyio
async def test_start_playback(fake_client, mcp_server):
    fake_client.set_response("start_playback", {"playing": True})

    content, _ = await mcp_server.call_tool("start_playback", {})
    result = json.loads(content[0].text)

    assert result["playing"] is True
    assert fake_client.commands_sent == [("start_playback", {})]


@pytest.mark.anyio
async def test_stop_playback(fake_client, mcp_server):
    fake_client.set_response("stop_playback", {"playing": False})

    content, _ = await mcp_server.call_tool("stop_playback", {})
    result = json.loads(content[0].text)

    assert result["playing"] is False


@pytest.mark.anyio
async def test_set_tempo(fake_client, mcp_server):
    fake_client.set_response("set_tempo", {"tempo": 140.0})

    content, _ = await mcp_server.call_tool("set_tempo", {"tempo": 140.0})
    result = json.loads(content[0].text)

    assert result["tempo"] == 140.0
    assert fake_client.commands_sent == [("set_tempo", {"tempo": 140.0})]
