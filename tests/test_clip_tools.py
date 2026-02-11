import json

import pytest


@pytest.mark.anyio
async def test_create_clip(fake_client, mcp_server):
    fake_client.set_response("create_clip", {"track_index": 0, "clip_index": 0})

    content, _ = await mcp_server.call_tool(
        "create_clip", {"track_index": 0, "clip_index": 0, "length": 8.0}
    )
    result = json.loads(content[0].text)

    assert result["track_index"] == 0
    assert fake_client.commands_sent == [
        ("create_clip", {"track_index": 0, "clip_index": 0, "length": 8.0})
    ]


@pytest.mark.anyio
async def test_create_clip_default_length(fake_client, mcp_server):
    fake_client.set_response("create_clip", {"track_index": 0, "clip_index": 0})

    await mcp_server.call_tool("create_clip", {"track_index": 0, "clip_index": 0})

    assert fake_client.commands_sent == [
        ("create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0})
    ]


@pytest.mark.anyio
async def test_add_notes_to_clip(fake_client, mcp_server):
    notes = [
        {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100},
        {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 80},
    ]
    fake_client.set_response("add_notes_to_clip", {"notes_added": 2})

    content, _ = await mcp_server.call_tool(
        "add_notes_to_clip",
        {"track_index": 0, "clip_index": 0, "notes": notes},
    )
    result = json.loads(content[0].text)

    assert result["notes_added"] == 2
    assert fake_client.commands_sent[0] == (
        "add_notes_to_clip",
        {"track_index": 0, "clip_index": 0, "notes": notes},
    )


@pytest.mark.anyio
async def test_set_clip_name(fake_client, mcp_server):
    fake_client.set_response("set_clip_name", {"name": "Melody A"})

    content, _ = await mcp_server.call_tool(
        "set_clip_name",
        {"track_index": 0, "clip_index": 0, "name": "Melody A"},
    )
    result = json.loads(content[0].text)

    assert result["name"] == "Melody A"


@pytest.mark.anyio
async def test_fire_clip(fake_client, mcp_server):
    fake_client.set_response("fire_clip", {"fired": True})

    content, _ = await mcp_server.call_tool(
        "fire_clip", {"track_index": 0, "clip_index": 0}
    )
    result = json.loads(content[0].text)

    assert result["fired"] is True


@pytest.mark.anyio
async def test_stop_clip(fake_client, mcp_server):
    fake_client.set_response("stop_clip", {"stopped": True})

    content, _ = await mcp_server.call_tool(
        "stop_clip", {"track_index": 1, "clip_index": 2}
    )
    result = json.loads(content[0].text)

    assert result["stopped"] is True
    assert fake_client.commands_sent == [
        ("stop_clip", {"track_index": 1, "clip_index": 2})
    ]
