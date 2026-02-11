import json

import pytest


@pytest.mark.anyio
async def test_get_browser_tree(fake_client, mcp_server):
    fake_client.set_response(
        "get_browser_tree",
        {
            "categories": [
                {"name": "Instruments", "children": ["Analog", "Wavetable"]},
                {"name": "Audio Effects", "children": ["Reverb", "Delay"]},
            ]
        },
    )

    content, _ = await mcp_server.call_tool(
        "get_browser_tree", {"category_type": "all"}
    )
    result = json.loads(content[0].text)

    assert len(result["categories"]) == 2
    assert fake_client.commands_sent == [("get_browser_tree", {"category_type": "all"})]


@pytest.mark.anyio
async def test_get_browser_items_at_path(fake_client, mcp_server):
    fake_client.set_response(
        "get_browser_items_at_path",
        {"items": [{"name": "Analog", "uri": "ableton:Analog"}]},
    )

    content, _ = await mcp_server.call_tool(
        "get_browser_items_at_path", {"path": "Instruments"}
    )
    result = json.loads(content[0].text)

    assert result["items"][0]["name"] == "Analog"


@pytest.mark.anyio
async def test_load_instrument_or_effect(fake_client, mcp_server):
    fake_client.set_response("load_browser_item", {"loaded": True})

    content, _ = await mcp_server.call_tool(
        "load_instrument_or_effect",
        {"track_index": 0, "uri": "ableton:Analog"},
    )
    result = json.loads(content[0].text)

    assert result["loaded"] is True
    assert fake_client.commands_sent == [
        ("load_browser_item", {"track_index": 0, "uri": "ableton:Analog"})
    ]


@pytest.mark.anyio
async def test_create_midi_track_with_instrument(fake_client, mcp_server):
    fake_client.set_response(
        "create_midi_track_with_instrument",
        {
            "track_index": 3,
            "name": "Bass",
            "uri": "ableton:Analog",
            "device_name": "Analog",
        },
    )

    content, _ = await mcp_server.call_tool(
        "create_midi_track_with_instrument",
        {"uri": "ableton:Analog", "index": -1, "name": "Bass"},
    )
    result = json.loads(content[0].text)

    assert result["track_index"] == 3
    assert result["name"] == "Bass"
    assert result["device_name"] == "Analog"
    assert fake_client.commands_sent == [
        (
            "create_midi_track_with_instrument",
            {"uri": "ableton:Analog", "index": -1, "name": "Bass"},
        )
    ]


@pytest.mark.anyio
async def test_load_drum_kit(fake_client, mcp_server):
    fake_client.set_response("load_browser_item", {"loaded": True})

    content, _ = await mcp_server.call_tool(
        "load_drum_kit",
        {
            "track_index": 0,
            "rack_uri": "ableton:DrumRack",
            "kit_path": "ableton:Kit808",
        },
    )
    result = json.loads(content[0].text)

    assert result["loaded"] is True
    assert len(fake_client.commands_sent) == 2
    assert fake_client.commands_sent[0] == (
        "load_browser_item",
        {"track_index": 0, "uri": "ableton:DrumRack"},
    )
    assert fake_client.commands_sent[1] == (
        "load_browser_item",
        {"track_index": 0, "uri": "ableton:Kit808"},
    )
