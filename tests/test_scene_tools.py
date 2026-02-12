import json

import pytest


@pytest.mark.anyio
async def test_create_scene(fake_client, mcp_server):
    fake_client.set_response("create_scene", {"index": 1, "name": ""})

    content, _ = await mcp_server.call_tool("create_scene", {"index": -1})
    result = json.loads(content[0].text)

    assert result["index"] == 1
    assert fake_client.commands_sent == [("create_scene", {"index": -1})]


@pytest.mark.anyio
async def test_delete_scene(fake_client, mcp_server):
    fake_client.set_response("delete_scene", {"deleted": True})

    content, _ = await mcp_server.call_tool("delete_scene", {"scene_index": 1})
    result = json.loads(content[0].text)

    assert result["deleted"] is True
    assert fake_client.commands_sent == [("delete_scene", {"scene_index": 1})]


@pytest.mark.anyio
async def test_set_scene_name(fake_client, mcp_server):
    fake_client.set_response("set_scene_name", {"name": "Verse"})

    content, _ = await mcp_server.call_tool(
        "set_scene_name", {"scene_index": 0, "name": "Verse"}
    )
    result = json.loads(content[0].text)

    assert result["name"] == "Verse"
    assert fake_client.commands_sent == [
        ("set_scene_name", {"scene_index": 0, "name": "Verse"})
    ]


@pytest.mark.anyio
async def test_fire_scene(fake_client, mcp_server):
    fake_client.set_response("fire_scene", {"fired": True})

    content, _ = await mcp_server.call_tool("fire_scene", {"scene_index": 0})
    result = json.loads(content[0].text)

    assert result["fired"] is True
    assert fake_client.commands_sent == [("fire_scene", {"scene_index": 0})]
