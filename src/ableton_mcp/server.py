from injector import Injector, Module, provider, singleton
from mcp.server.fastmcp import FastMCP


class Greeter:
    def greet(self) -> str:
        return "Hello from Ableton MCP!"


class AbletonModule(Module):
    @singleton
    @provider
    def provide_greeter(self) -> Greeter:
        return Greeter()


def create_server(injector: Injector | None = None) -> FastMCP:
    if injector is None:
        injector = Injector([AbletonModule])

    mcp = FastMCP("ableton-mcp")

    @mcp.tool()
    def hello() -> str:
        """Say hello from Ableton MCP."""
        greeter = injector.get(Greeter)
        return greeter.greet()

    return mcp


mcp = create_server()
