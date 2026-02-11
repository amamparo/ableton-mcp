import json

from injector import Injector, Module, provider, singleton
from mcp.server.fastmcp import FastMCP

from ableton_mcp.client import AbletonClient, SocketAbletonClient


class AbletonModule(Module):
    @singleton
    @provider
    def provide_ableton_client(self) -> AbletonClient:
        return SocketAbletonClient()


def create_server(injector: Injector | None = None) -> FastMCP:
    if injector is None:
        injector = Injector([AbletonModule])

    mcp = FastMCP("ableton-mcp")

    def _client() -> AbletonClient:
        return injector.get(AbletonClient)

    def _call(command_type: str, params: dict | None = None) -> str:
        try:
            result = _client().send_command(command_type, params)
            return json.dumps(result, indent=2)
        except RuntimeError as e:
            return json.dumps({"error": str(e)})

    # ── Session / Info ──────────────────────────────────────────────

    @mcp.tool()
    def get_session_info() -> str:
        """Get current Ableton Live session info: tempo, time signature,
        track counts, and master track details."""
        return _call("get_session_info")

    @mcp.tool()
    def get_track_info(track_index: int) -> str:
        """Get detailed info about a track: name, type, mute/solo/arm state,
        volume, pan, clip slots, and devices."""
        return _call("get_track_info", {"track_index": track_index})

    # ── Track Management ────────────────────────────────────────────

    @mcp.tool()
    def create_midi_track(index: int = -1) -> str:
        """Create a new MIDI track. Use index=-1 to append at the end."""
        return _call("create_midi_track", {"index": index})

    @mcp.tool()
    def create_audio_track(index: int = -1) -> str:
        """Create a new audio track. Use index=-1 to append at the end."""
        return _call("create_audio_track", {"index": index})

    @mcp.tool()
    def delete_track(track_index: int) -> str:
        """Delete a track by index."""
        return _call("delete_track", {"track_index": track_index})

    @mcp.tool()
    def set_track_name(track_index: int, name: str) -> str:
        """Rename a track."""
        return _call("set_track_name", {"track_index": track_index, "name": name})

    @mcp.tool()
    def set_track_volume(track_index: int, volume: float) -> str:
        """Set track volume. Range: 0.0 (silence) to 1.0 (max)."""
        return _call("set_track_volume", {"track_index": track_index, "volume": volume})

    @mcp.tool()
    def set_track_pan(track_index: int, pan: float) -> str:
        """Set track pan. Range: -1.0 (full left) to 1.0 (full right),
        0.0 is center."""
        return _call("set_track_pan", {"track_index": track_index, "pan": pan})

    @mcp.tool()
    def set_track_mute(track_index: int, mute: bool) -> str:
        """Mute or unmute a track."""
        return _call("set_track_mute", {"track_index": track_index, "mute": mute})

    @mcp.tool()
    def set_track_solo(track_index: int, solo: bool) -> str:
        """Solo or unsolo a track."""
        return _call("set_track_solo", {"track_index": track_index, "solo": solo})

    # ── Clip Operations ─────────────────────────────────────────────

    @mcp.tool()
    def create_clip(track_index: int, clip_index: int, length: float = 4.0) -> str:
        """Create an empty MIDI clip in a clip slot. Length is in beats."""
        return _call(
            "create_clip",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "length": length,
            },
        )

    @mcp.tool()
    def add_notes_to_clip(track_index: int, clip_index: int, notes: list[dict]) -> str:
        """Add MIDI notes to a clip. Each note is a dict with keys:
        pitch (0-127), start_time (beats), duration (beats),
        velocity (0-127, default 100), mute (bool, default false).
        Note: this replaces all existing notes in the clip."""
        return _call(
            "add_notes_to_clip",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "notes": notes,
            },
        )

    @mcp.tool()
    def set_clip_name(track_index: int, clip_index: int, name: str) -> str:
        """Rename a clip."""
        return _call(
            "set_clip_name",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "name": name,
            },
        )

    @mcp.tool()
    def fire_clip(track_index: int, clip_index: int) -> str:
        """Start playing a clip."""
        return _call(
            "fire_clip",
            {"track_index": track_index, "clip_index": clip_index},
        )

    @mcp.tool()
    def stop_clip(track_index: int, clip_index: int) -> str:
        """Stop a playing clip."""
        return _call(
            "stop_clip",
            {"track_index": track_index, "clip_index": clip_index},
        )

    # ── Transport ───────────────────────────────────────────────────

    @mcp.tool()
    def start_playback() -> str:
        """Start session playback."""
        return _call("start_playback")

    @mcp.tool()
    def stop_playback() -> str:
        """Stop session playback."""
        return _call("stop_playback")

    @mcp.tool()
    def set_tempo(tempo: float) -> str:
        """Set the session tempo in BPM."""
        return _call("set_tempo", {"tempo": tempo})

    # ── Browser / Devices ───────────────────────────────────────────

    @mcp.tool()
    def get_browser_tree(category_type: str = "all") -> str:
        """Browse Ableton's instrument and effect categories.
        category_type can be: all, instruments, audio_effects, midi_effects,
        sounds, drums, max_for_live."""
        return _call("get_browser_tree", {"category_type": category_type})

    @mcp.tool()
    def get_browser_items_at_path(path: str) -> str:
        """List items at a specific browser path (e.g. 'Instruments/Analog').
        Use get_browser_tree first to discover available categories."""
        return _call("get_browser_items_at_path", {"path": path})

    @mcp.tool()
    def load_instrument_or_effect(track_index: int, uri: str) -> str:
        """Load an instrument or effect onto a track by its browser URI.
        Use get_browser_tree and get_browser_items_at_path to find URIs."""
        return _call(
            "load_browser_item",
            {"track_index": track_index, "uri": uri},
        )

    @mcp.tool()
    def load_drum_kit(track_index: int, rack_uri: str, kit_path: str) -> str:
        """Load a drum rack and then load a specific kit into it.
        First loads the rack by URI, then navigates to kit_path to load
        the kit preset."""
        _call(
            "load_browser_item",
            {"track_index": track_index, "uri": rack_uri},
        )
        return _call(
            "load_browser_item",
            {"track_index": track_index, "uri": kit_path},
        )

    return mcp


mcp = create_server()
