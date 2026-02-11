import json

import pytest


@pytest.mark.anyio
async def test_get_arrangement_clips(fake_client, mcp_server):
    fake_client.set_response(
        "get_arrangement_clips",
        {
            "clips": [
                {
                    "index": 0,
                    "name": "Intro",
                    "start_time": 0.0,
                    "end_time": 16.0,
                    "length": 16.0,
                    "is_playing": False,
                },
                {
                    "index": 1,
                    "name": "Verse",
                    "start_time": 16.0,
                    "end_time": 48.0,
                    "length": 32.0,
                    "is_playing": False,
                },
            ]
        },
    )

    content, _ = await mcp_server.call_tool("get_arrangement_clips", {"track_index": 0})
    result = json.loads(content[0].text)

    assert len(result["clips"]) == 2
    assert result["clips"][0]["name"] == "Intro"
    assert result["clips"][1]["start_time"] == 16.0
    assert fake_client.commands_sent == [("get_arrangement_clips", {"track_index": 0})]


@pytest.mark.anyio
async def test_create_arrangement_clip(fake_client, mcp_server):
    fake_client.set_response(
        "create_arrangement_clip",
        {"track_index": 0, "start_time": 8.0, "length": 4.0},
    )

    content, _ = await mcp_server.call_tool(
        "create_arrangement_clip",
        {"track_index": 0, "start_time": 8.0, "length": 4.0},
    )
    result = json.loads(content[0].text)

    assert result["start_time"] == 8.0
    assert result["length"] == 4.0
    assert fake_client.commands_sent == [
        (
            "create_arrangement_clip",
            {"track_index": 0, "start_time": 8.0, "length": 4.0},
        )
    ]


@pytest.mark.anyio
async def test_delete_arrangement_clip(fake_client, mcp_server):
    fake_client.set_response("delete_arrangement_clip", {"deleted": True})

    content, _ = await mcp_server.call_tool(
        "delete_arrangement_clip", {"track_index": 0, "clip_index": 1}
    )
    result = json.loads(content[0].text)

    assert result["deleted"] is True


@pytest.mark.anyio
async def test_duplicate_arrangement_clip(fake_client, mcp_server):
    fake_client.set_response(
        "duplicate_arrangement_clip",
        {"duplicated": True, "destination_time": 32.0},
    )

    content, _ = await mcp_server.call_tool(
        "duplicate_arrangement_clip",
        {"track_index": 0, "clip_index": 0, "destination_time": 32.0},
    )
    result = json.loads(content[0].text)

    assert result["duplicated"] is True
    assert result["destination_time"] == 32.0


@pytest.mark.anyio
async def test_get_arrangement_clip_notes(fake_client, mcp_server):
    fake_client.set_response(
        "get_arrangement_clip_notes",
        {
            "notes": [
                {
                    "pitch": 60,
                    "start_time": 0.0,
                    "duration": 1.0,
                    "velocity": 100,
                    "mute": False,
                }
            ]
        },
    )

    content, _ = await mcp_server.call_tool(
        "get_arrangement_clip_notes", {"track_index": 0, "clip_index": 0}
    )
    result = json.loads(content[0].text)

    assert len(result["notes"]) == 1
    assert result["notes"][0]["pitch"] == 60


@pytest.mark.anyio
async def test_set_arrangement_clip_notes(fake_client, mcp_server):
    notes = [
        {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100},
        {"pitch": 67, "start_time": 0.5, "duration": 0.5, "velocity": 80},
    ]
    fake_client.set_response("set_arrangement_clip_notes", {"notes_set": 2})

    content, _ = await mcp_server.call_tool(
        "set_arrangement_clip_notes",
        {"track_index": 0, "clip_index": 0, "notes": notes},
    )
    result = json.loads(content[0].text)

    assert result["notes_set"] == 2


@pytest.mark.anyio
async def test_set_song_time(fake_client, mcp_server):
    fake_client.set_response("set_song_time", {"current_song_time": 16.0})

    content, _ = await mcp_server.call_tool("set_song_time", {"time": 16.0})
    result = json.loads(content[0].text)

    assert result["current_song_time"] == 16.0
    assert fake_client.commands_sent == [("set_song_time", {"time": 16.0})]


@pytest.mark.anyio
async def test_get_arrangement_loop(fake_client, mcp_server):
    fake_client.set_response(
        "get_arrangement_loop", {"loop_start": 0.0, "loop_length": 16.0}
    )

    content, _ = await mcp_server.call_tool("get_arrangement_loop", {})
    result = json.loads(content[0].text)

    assert result["loop_start"] == 0.0
    assert result["loop_length"] == 16.0


@pytest.mark.anyio
async def test_set_arrangement_loop(fake_client, mcp_server):
    fake_client.set_response(
        "set_arrangement_loop", {"loop_start": 8.0, "loop_length": 32.0}
    )

    content, _ = await mcp_server.call_tool(
        "set_arrangement_loop", {"start": 8.0, "length": 32.0}
    )
    result = json.loads(content[0].text)

    assert result["loop_start"] == 8.0
    assert result["loop_length"] == 32.0


@pytest.mark.anyio
async def test_back_to_arranger(fake_client, mcp_server):
    fake_client.set_response("back_to_arranger", {"back_to_arranger": True})

    content, _ = await mcp_server.call_tool("back_to_arranger", {})
    result = json.loads(content[0].text)

    assert result["back_to_arranger"] is True


@pytest.mark.anyio
async def test_duplicate_session_to_arrangement(fake_client, mcp_server):
    fake_client.set_response(
        "duplicate_session_to_arrangement",
        {
            "duplicated": True,
            "track_index": 0,
            "clip_index": 0,
            "destination_time": 0.0,
        },
    )

    content, _ = await mcp_server.call_tool(
        "duplicate_session_to_arrangement",
        {"track_index": 0, "clip_index": 0, "destination_time": 0.0},
    )
    result = json.loads(content[0].text)

    assert result["duplicated"] is True


@pytest.mark.anyio
async def test_session_to_arrangement(fake_client, mcp_server):
    fake_client.set_response(
        "session_to_arrangement",
        {"clips_placed": 6, "total_length": 64.0, "scenes_processed": 3},
    )

    content, _ = await mcp_server.call_tool(
        "session_to_arrangement", {"scene_indices": [0, 1, 2]}
    )
    result = json.loads(content[0].text)

    assert result["clips_placed"] == 6
    assert result["total_length"] == 64.0
    assert result["scenes_processed"] == 3
    assert fake_client.commands_sent == [
        ("session_to_arrangement", {"scene_indices": [0, 1, 2]})
    ]
