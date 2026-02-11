# ableton-mcp

MCP server for Ableton Live.

## Integration

### Claude Desktop

Add to your `claude_desktop_config.json`:

**Latest (main):**
```json
{
  "mcpServers": {
    "ableton-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/amamparo/ableton-mcp", "ableton-mcp"]
    }
  }
}
```

**Pinned to a tag:**
```json
{
  "mcpServers": {
    "ableton-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/amamparo/ableton-mcp@v0.1.0", "ableton-mcp"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add ableton-mcp -- uvx --from "git+https://github.com/amamparo/ableton-mcp" ableton-mcp
```

## Development

```bash
just install   # Install dependencies
just check     # Run lint + tests
just fmt       # Auto-format code
```
