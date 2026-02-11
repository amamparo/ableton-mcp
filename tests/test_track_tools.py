import json

import pytest


@pytest.mark.anyio
async def test_create_midi_track(fake_client, mcp_server):
    fake_client.set_response("create_midi_track", {"index": 3, "name": "MIDI 4"})

    content, _ = await mcp_server.call_tool("create_midi_track", {"index": -1})
    result = json.loads(content[0].text)

    assert result["name"] == "MIDI 4"
    assert fake_client.commands_sent == [("create_midi_track", {"index": -1})]


@pytest.mark.anyio
async def test_create_audio_track(fake_client, mcp_server):
    fake_client.set_response("create_audio_track", {"index": 0, "name": "Audio 1"})

    content, _ = await mcp_server.call_tool("create_audio_track", {"index": 0})
    result = json.loads(content[0].text)

    assert result["name"] == "Audio 1"


@pytest.mark.anyio
async def test_delete_track(fake_client, mcp_server):
    fake_client.set_response("delete_track", {"deleted": True})

    content, _ = await mcp_server.call_tool("delete_track", {"track_index": 2})
    result = json.loads(content[0].text)

    assert result["deleted"] is True
    assert fake_client.commands_sent == [("delete_track", {"track_index": 2})]


@pytest.mark.anyio
async def test_set_track_name(fake_client, mcp_server):
    fake_client.set_response("set_track_name", {"name": "Kick"})

    content, _ = await mcp_server.call_tool(
        "set_track_name", {"track_index": 0, "name": "Kick"}
    )
    result = json.loads(content[0].text)

    assert result["name"] == "Kick"


@pytest.mark.anyio
async def test_set_track_volume(fake_client, mcp_server):
    fake_client.set_response("set_track_volume", {"volume": 0.75})

    content, _ = await mcp_server.call_tool(
        "set_track_volume", {"track_index": 1, "volume": 0.75}
    )
    result = json.loads(content[0].text)

    assert result["volume"] == 0.75


@pytest.mark.anyio
async def test_set_track_pan(fake_client, mcp_server):
    fake_client.set_response("set_track_pan", {"pan": -0.5})

    content, _ = await mcp_server.call_tool(
        "set_track_pan", {"track_index": 0, "pan": -0.5}
    )
    result = json.loads(content[0].text)

    assert result["pan"] == -0.5


@pytest.mark.anyio
async def test_set_track_mute(fake_client, mcp_server):
    fake_client.set_response("set_track_mute", {"mute": True})

    content, _ = await mcp_server.call_tool(
        "set_track_mute", {"track_index": 0, "mute": True}
    )
    result = json.loads(content[0].text)

    assert result["mute"] is True
    assert fake_client.commands_sent == [
        ("set_track_mute", {"track_index": 0, "mute": True})
    ]


@pytest.mark.anyio
async def test_set_track_solo(fake_client, mcp_server):
    fake_client.set_response("set_track_solo", {"solo": True})

    content, _ = await mcp_server.call_tool(
        "set_track_solo", {"track_index": 2, "solo": True}
    )
    result = json.loads(content[0].text)

    assert result["solo"] is True
