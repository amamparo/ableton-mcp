import pytest
from injector import Injector, Module, provider, singleton

from ableton_mcp.server import Greeter, create_server


@pytest.mark.anyio
async def test_hello_tool():
    """Test that the hello tool returns the expected greeting."""
    mcp = create_server()
    content, _ = await mcp.call_tool("hello", {})
    assert content[0].text == "Hello from Ableton MCP!"


@pytest.mark.anyio
async def test_hello_tool_with_custom_greeter():
    """Test that dependency injection allows swapping implementations."""

    class FakeGreeter(Greeter):
        def greet(self) -> str:
            return "Fake hello!"

    class TestModule(Module):
        @singleton
        @provider
        def provide_greeter(self) -> Greeter:
            return FakeGreeter()

    injector = Injector([TestModule])
    mcp = create_server(injector)
    content, _ = await mcp.call_tool("hello", {})
    assert content[0].text == "Fake hello!"


@pytest.mark.anyio
async def test_list_tools():
    """Test that the server exposes the hello tool."""
    mcp = create_server()
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "hello" in tool_names
