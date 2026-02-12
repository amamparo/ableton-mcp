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
    def delete_all_tracks() -> str:
        """Delete all tracks except one. Useful for clearing a session before
        building a fresh arrangement. Returns the count of deleted tracks."""
        return _call("delete_all_tracks")

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

    @mcp.tool()
    def get_clip_notes(track_index: int, clip_index: int) -> str:
        """Read all MIDI notes from a session clip.
        Returns a list of notes with pitch, start_time, duration, velocity,
        and mute."""
        return _call(
            "get_clip_notes",
            {"track_index": track_index, "clip_index": clip_index},
        )

    @mcp.tool()
    def get_clip_info(track_index: int, clip_index: int) -> str:
        """Get detailed info about a session clip: name, length,
        loop_start, loop_end, is_playing, is_recording."""
        return _call(
            "get_clip_info",
            {"track_index": track_index, "clip_index": clip_index},
        )

    @mcp.tool()
    def duplicate_clip_to_scene(
        track_index: int, source_clip_index: int, dest_clip_index: int
    ) -> str:
        """Duplicate a session clip from one scene to another on the same track.
        The destination clip slot must be empty."""
        return _call(
            "duplicate_clip_to_scene",
            {
                "track_index": track_index,
                "source_clip_index": source_clip_index,
                "dest_clip_index": dest_clip_index,
            },
        )

    @mcp.tool()
    def delete_clip(track_index: int, clip_index: int) -> str:
        """Delete a clip from a session clip slot."""
        return _call(
            "delete_clip",
            {"track_index": track_index, "clip_index": clip_index},
        )

    # ── Scene Management ─────────────────────────────────────────────

    @mcp.tool()
    def create_scene(index: int = -1) -> str:
        """Create a new empty scene. Use index=-1 to append at the end.
        Adds a new clip slot row across all tracks."""
        return _call("create_scene", {"index": index})

    @mcp.tool()
    def delete_scene(scene_index: int) -> str:
        """Delete a scene by index. Cannot delete the last scene."""
        return _call("delete_scene", {"scene_index": scene_index})

    @mcp.tool()
    def set_scene_name(scene_index: int, name: str) -> str:
        """Rename a scene (the label in the Master track column)."""
        return _call("set_scene_name", {"scene_index": scene_index, "name": name})

    @mcp.tool()
    def fire_scene(scene_index: int) -> str:
        """Fire all clips in a scene simultaneously."""
        return _call("fire_scene", {"scene_index": scene_index})

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

    @mcp.tool()
    def set_time_signature(numerator: int, denominator: int) -> str:
        """Set the song's time signature (e.g. 4/4, 5/4, 7/8)."""
        return _call(
            "set_time_signature",
            {"numerator": numerator, "denominator": denominator},
        )

    @mcp.tool()
    def undo() -> str:
        """Trigger Ableton's undo. Safety net for destructive operations."""
        return _call("undo")

    # ── Browser / Devices ───────────────────────────────────────────

    @mcp.tool()
    def get_browser_tree(category_type: str = "all") -> str:
        """Browse Ableton's instrument and effect categories.
        category_type can be: all, instruments, audio_effects, midi_effects,
        sounds, drums, max_for_live."""
        return _call("get_browser_tree", {"category_type": category_type})

    @mcp.tool()
    def get_browser_items_at_path(path: str) -> str:
        """List items at a browser path. Paths can start with a top-level category
        (e.g. 'Sounds/Bass', 'Instruments/Analog', 'Audio Effects/Reverb') or
        use a bare subcategory name (e.g. 'Bass').
        Use get_browser_tree first to discover available categories."""
        return _call("get_browser_items_at_path", {"path": path})

    @mcp.tool()
    def load_instrument_or_effect(track_index: int, uri: str) -> str:
        """Load an instrument or effect onto a track by its browser URI.
        Use get_browser_tree and get_browser_items_at_path to find URIs.
        Returns the loaded device_name so you can verify the correct device was loaded.
        """
        return _call(
            "load_browser_item",
            {"track_index": track_index, "uri": uri},
        )

    @mcp.tool()
    def create_midi_track_with_instrument(
        uri: str, index: int = -1, name: str = ""
    ) -> str:
        """Create a new MIDI track and load an instrument in a single operation.
        Faster than separate create_midi_track + load_instrument_or_effect calls.
        Use index=-1 to append at the end. Optionally set the track name."""
        params: dict = {"uri": uri, "index": index}
        if name:
            params["name"] = name
        return _call("create_midi_track_with_instrument", params)

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

    # ── Device Parameters ────────────────────────────────────────────

    @mcp.tool()
    def get_device_parameters(track_index: int, device_index: int) -> str:
        """List all parameters of a device on a track.
        Returns device_name and a list of parameters with name, value, min, max."""
        return _call(
            "get_device_parameters",
            {"track_index": track_index, "device_index": device_index},
        )

    @mcp.tool()
    def set_device_parameter(
        track_index: int, device_index: int, param_index: int, value: float
    ) -> str:
        """Set a device parameter value. Value is clamped to the parameter's
        min/max range. Use get_device_parameters to discover available parameters."""
        return _call(
            "set_device_parameter",
            {
                "track_index": track_index,
                "device_index": device_index,
                "param_index": param_index,
                "value": value,
            },
        )

    # ── Arrangement View ─────────────────────────────────────────────

    @mcp.tool()
    def get_arrangement_clips(track_index: int) -> str:
        """Get all clips on the arrangement timeline for a track.
        Returns each clip's index, name, start_time, end_time, and length
        in beats. Requires Ableton Live 11+."""
        return _call("get_arrangement_clips", {"track_index": track_index})

    @mcp.tool()
    def create_arrangement_clip(
        track_index: int, start_time: float, length: float
    ) -> str:
        """Create an empty MIDI clip on the arrangement timeline.
        start_time and length are in beats."""
        return _call(
            "create_arrangement_clip",
            {
                "track_index": track_index,
                "start_time": start_time,
                "length": length,
            },
        )

    @mcp.tool()
    def delete_arrangement_clip(track_index: int, clip_index: int) -> str:
        """Delete a clip from the arrangement timeline.
        Use get_arrangement_clips to find the clip_index."""
        return _call(
            "delete_arrangement_clip",
            {"track_index": track_index, "clip_index": clip_index},
        )

    @mcp.tool()
    def duplicate_arrangement_clip(
        track_index: int, clip_index: int, destination_time: float
    ) -> str:
        """Duplicate an arrangement clip to a new position on the timeline.
        destination_time is in beats."""
        return _call(
            "duplicate_arrangement_clip",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "destination_time": destination_time,
            },
        )

    @mcp.tool()
    def get_arrangement_clip_notes(track_index: int, clip_index: int) -> str:
        """Read all MIDI notes from an arrangement clip.
        Returns a list of notes with pitch, start_time, duration, velocity,
        and mute."""
        return _call(
            "get_arrangement_clip_notes",
            {"track_index": track_index, "clip_index": clip_index},
        )

    @mcp.tool()
    def set_arrangement_clip_notes(
        track_index: int, clip_index: int, notes: list[dict]
    ) -> str:
        """Set MIDI notes on an arrangement clip. Replaces all existing notes.
        Each note is a dict with keys: pitch (0-127), start_time (beats),
        duration (beats), velocity (0-127, default 100), mute (bool, default false)."""
        return _call(
            "set_arrangement_clip_notes",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "notes": notes,
            },
        )

    @mcp.tool()
    def set_song_time(time: float) -> str:
        """Set the playback cursor position in beats."""
        return _call("set_song_time", {"time": time})

    @mcp.tool()
    def get_arrangement_loop() -> str:
        """Get the arrangement loop brace position and length in beats."""
        return _call("get_arrangement_loop")

    @mcp.tool()
    def set_arrangement_loop(start: float, length: float) -> str:
        """Set the arrangement loop brace. start and length are in beats."""
        return _call("set_arrangement_loop", {"start": start, "length": length})

    @mcp.tool()
    def back_to_arranger() -> str:
        """Switch playback from session view back to the arrangement.
        Stops all session clips and resumes arrangement playback."""
        return _call("back_to_arranger")

    @mcp.tool()
    def duplicate_session_to_arrangement(
        track_index: int, clip_index: int, destination_time: float
    ) -> str:
        """Copy a session view clip to the arrangement timeline.
        destination_time is the position in beats where the clip will be placed."""
        return _call(
            "duplicate_session_to_arrangement",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "destination_time": destination_time,
            },
        )

    @mcp.tool()
    def session_to_arrangement(scene_indices: list[int]) -> str:
        """Lay out session view scenes sequentially on the arrangement timeline.
        Takes a list of scene indices and places each scene's clips end-to-end
        starting from beat 0. Use this to build a full song structure from
        session view clips."""
        return _call("session_to_arrangement", {"scene_indices": scene_indices})

    return mcp


mcp = create_server()
