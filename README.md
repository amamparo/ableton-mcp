# ableton-mcp

MCP server for controlling Ableton Live — enabling AI assistants to interact with Live sessions via the Model Context Protocol.

## Prerequisites

- **Ableton Live 10+**

## Setup

### 1. Install the Control Surface

A control surface script must be installed into Ableton Live. It runs inside Live and exposes a TCP socket for the MCP server to connect to.

**macOS:**

```bash
mkdir -p ~/Music/Ableton/User\ Library/Remote\ Scripts/AbletonMCP && curl -fsSL https://raw.githubusercontent.com/amamparo/ableton-mcp/main/control_surface/AbletonMCP/__init__.py -o ~/Music/Ableton/User\ Library/Remote\ Scripts/AbletonMCP/__init__.py
```

**Windows (PowerShell):**

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Documents\Ableton\User Library\Remote Scripts\AbletonMCP" | Out-Null; Invoke-WebRequest -Uri "https://raw.githubusercontent.com/amamparo/ableton-mcp/main/control_surface/AbletonMCP/__init__.py" -OutFile "$env:USERPROFILE\Documents\Ableton\User Library\Remote Scripts\AbletonMCP\__init__.py"
```

### 2. Enable in Ableton Live

1. Open (or restart) Ableton Live
2. Go to **Preferences** > **Link, Tempo & MIDI**
3. Under **Control Surface**, select **AbletonMCP** from the dropdown
4. You should see "AbletonMCP: Listening on port 9877" in Ableton's log

### 3. Configure the MCP Client

**Claude Desktop** — add to `claude_desktop_config.json`:

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

To pin to a specific version:

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

**Claude Code:**

```bash
claude mcp add ableton-mcp -- uvx --from "git+https://github.com/amamparo/ableton-mcp" ableton-mcp
```

## Available Tools

| Tool | Description |
|------|-------------|
| `get_session_info` | Get tempo, time signature, track counts |
| `get_track_info` | Get track details (name, volume, pan, clips, devices) |
| `create_midi_track` | Create a new MIDI track |
| `create_audio_track` | Create a new audio track |
| `delete_track` | Delete a track |
| `set_track_name` | Rename a track |
| `set_track_volume` | Set track volume (0.0–1.0) |
| `set_track_pan` | Set track pan (-1.0–1.0) |
| `set_track_mute` | Mute/unmute a track |
| `set_track_solo` | Solo/unsolo a track |
| `create_clip` | Create an empty MIDI clip |
| `add_notes_to_clip` | Add MIDI notes to a clip |
| `set_clip_name` | Rename a clip |
| `fire_clip` | Start playing a clip |
| `stop_clip` | Stop a clip |
| `start_playback` | Start session playback |
| `stop_playback` | Stop session playback |
| `set_tempo` | Set tempo in BPM |
| `get_browser_tree` | Browse instruments/effects categories |
| `get_browser_items_at_path` | List items at a browser path |
| `load_instrument_or_effect` | Load a device onto a track |
| `load_drum_kit` | Load a drum rack and kit |
| `get_arrangement_clips` | List clips on the arrangement timeline |
| `create_arrangement_clip` | Create a MIDI clip on the arrangement timeline |
| `delete_arrangement_clip` | Delete an arrangement clip |
| `duplicate_arrangement_clip` | Duplicate an arrangement clip to a new position |
| `get_arrangement_clip_notes` | Read MIDI notes from an arrangement clip |
| `set_arrangement_clip_notes` | Set MIDI notes on an arrangement clip |
| `set_song_time` | Set the playback cursor position |
| `get_arrangement_loop` | Get the arrangement loop brace |
| `set_arrangement_loop` | Set the arrangement loop brace |
| `back_to_arranger` | Switch from session to arrangement playback |
| `duplicate_session_to_arrangement` | Copy a session clip to the arrangement |
| `session_to_arrangement` | Lay out scenes sequentially on the arrangement |

> **Note:** Automation breakpoints are not available via the control surface API. Arrangement view features require Ableton Live 11+.

## Development

```bash
just install                  # Install dependencies
just check                    # Run lint + tests
just fmt                      # Auto-format code
just install-control-surface  # Install control surface to Ableton
```
