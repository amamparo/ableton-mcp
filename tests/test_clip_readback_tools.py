import json

import pytest


@pytest.mark.anyio
async def test_get_clip_notes(fake_client, mcp_server):
    fake_client.set_response(
        "get_clip_notes",
        {
            "notes": [
                {
                    "pitch": 60,
                    "start_time": 0.0,
                    "duration": 1.0,
                    "velocity": 100,
                    "mute": False,
                },
                {
                    "pitch": 64,
                    "start_time": 1.0,
                    "duration": 0.5,
                    "velocity": 80,
                    "mute": False,
                },
            ]
        },
    )

    content, _ = await mcp_server.call_tool(
        "get_clip_notes", {"track_index": 0, "clip_index": 0}
    )
    result = json.loads(content[0].text)

    assert len(result["notes"]) == 2
    assert result["notes"][0]["pitch"] == 60
    assert result["notes"][1]["velocity"] == 80
    assert fake_client.commands_sent == [
        ("get_clip_notes", {"track_index": 0, "clip_index": 0})
    ]


@pytest.mark.anyio
async def test_get_clip_info(fake_client, mcp_server):
    fake_client.set_response(
        "get_clip_info",
        {
            "name": "Verse",
            "length": 16.0,
            "loop_start": 0.0,
            "loop_end": 16.0,
            "is_playing": False,
            "is_recording": False,
        },
    )

    content, _ = await mcp_server.call_tool(
        "get_clip_info", {"track_index": 0, "clip_index": 0}
    )
    result = json.loads(content[0].text)

    assert result["name"] == "Verse"
    assert result["length"] == 16.0
    assert result["loop_start"] == 0.0


@pytest.mark.anyio
async def test_duplicate_clip_to_scene(fake_client, mcp_server):
    fake_client.set_response(
        "duplicate_clip_to_scene",
        {
            "duplicated": True,
            "track_index": 0,
            "source_clip_index": 0,
            "dest_clip_index": 1,
        },
    )

    content, _ = await mcp_server.call_tool(
        "duplicate_clip_to_scene",
        {"track_index": 0, "source_clip_index": 0, "dest_clip_index": 1},
    )
    result = json.loads(content[0].text)

    assert result["duplicated"] is True
    assert fake_client.commands_sent == [
        (
            "duplicate_clip_to_scene",
            {"track_index": 0, "source_clip_index": 0, "dest_clip_index": 1},
        )
    ]


@pytest.mark.anyio
async def test_delete_clip(fake_client, mcp_server):
    fake_client.set_response("delete_clip", {"deleted": True})

    content, _ = await mcp_server.call_tool(
        "delete_clip", {"track_index": 0, "clip_index": 0}
    )
    result = json.loads(content[0].text)

    assert result["deleted"] is True
    assert fake_client.commands_sent == [
        ("delete_clip", {"track_index": 0, "clip_index": 0})
    ]
