import json

import pytest


@pytest.mark.anyio
async def test_set_time_signature(fake_client, mcp_server):
    fake_client.set_response(
        "set_time_signature",
        {"signature_numerator": 5, "signature_denominator": 4},
    )

    content, _ = await mcp_server.call_tool(
        "set_time_signature", {"numerator": 5, "denominator": 4}
    )
    result = json.loads(content[0].text)

    assert result["signature_numerator"] == 5
    assert result["signature_denominator"] == 4
    assert fake_client.commands_sent == [
        ("set_time_signature", {"numerator": 5, "denominator": 4})
    ]


@pytest.mark.anyio
async def test_get_device_parameters(fake_client, mcp_server):
    fake_client.set_response(
        "get_device_parameters",
        {
            "device_name": "Analog",
            "parameters": [
                {"index": 0, "name": "Device On", "value": 1.0, "min": 0.0, "max": 1.0},
                {
                    "index": 1,
                    "name": "Filter Freq",
                    "value": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                },
            ],
        },
    )

    content, _ = await mcp_server.call_tool(
        "get_device_parameters", {"track_index": 0, "device_index": 0}
    )
    result = json.loads(content[0].text)

    assert result["device_name"] == "Analog"
    assert len(result["parameters"]) == 2
    assert result["parameters"][1]["name"] == "Filter Freq"
    assert fake_client.commands_sent == [
        ("get_device_parameters", {"track_index": 0, "device_index": 0})
    ]


@pytest.mark.anyio
async def test_set_device_parameter(fake_client, mcp_server):
    fake_client.set_response(
        "set_device_parameter", {"name": "Filter Freq", "value": 0.75}
    )

    content, _ = await mcp_server.call_tool(
        "set_device_parameter",
        {"track_index": 0, "device_index": 0, "param_index": 1, "value": 0.75},
    )
    result = json.loads(content[0].text)

    assert result["name"] == "Filter Freq"
    assert result["value"] == 0.75
    assert fake_client.commands_sent == [
        (
            "set_device_parameter",
            {
                "track_index": 0,
                "device_index": 0,
                "param_index": 1,
                "value": 0.75,
            },
        )
    ]


@pytest.mark.anyio
async def test_undo(fake_client, mcp_server):
    fake_client.set_response("undo", {"undone": True})

    content, _ = await mcp_server.call_tool("undo", {})
    result = json.loads(content[0].text)

    assert result["undone"] is True
    assert fake_client.commands_sent == [("undo", {})]
