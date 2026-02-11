from __future__ import absolute_import

import json
import socket
import threading
import traceback

try:
    import Queue as queue
except ImportError:
    import queue

from _Framework.ControlSurface import ControlSurface

HOST = "127.0.0.1"
PORT = 9877


def create_instance(c_instance):
    return AbletonMCP(c_instance)


class AbletonMCP(ControlSurface):

    # Registry: command_type -> (method_name, requires_main_thread)
    COMMANDS = {
        # Read-only (safe on socket thread)
        "get_session_info": ("_get_session_info", False),
        "get_track_info": ("_get_track_info", False),
        "get_browser_tree": ("_get_browser_tree", False),
        "get_browser_items_at_path": ("_get_browser_items_at_path", False),
        # State-modifying (must run on main thread)
        "create_midi_track": ("_create_midi_track", True),
        "create_audio_track": ("_create_audio_track", True),
        "delete_track": ("_delete_track", True),
        "set_track_name": ("_set_track_name", True),
        "set_track_volume": ("_set_track_volume", True),
        "set_track_pan": ("_set_track_pan", True),
        "set_track_mute": ("_set_track_mute", True),
        "set_track_solo": ("_set_track_solo", True),
        "create_clip": ("_create_clip", True),
        "add_notes_to_clip": ("_add_notes_to_clip", True),
        "set_clip_name": ("_set_clip_name", True),
        "fire_clip": ("_fire_clip", True),
        "stop_clip": ("_stop_clip", True),
        "start_playback": ("_start_playback", True),
        "stop_playback": ("_stop_playback", True),
        "set_tempo": ("_set_tempo", True),
        "load_browser_item": ("_load_browser_item", True),
        # Arrangement view
        "get_arrangement_clips": ("_get_arrangement_clips", False),
        "create_arrangement_clip": ("_create_arrangement_clip", True),
        "delete_arrangement_clip": ("_delete_arrangement_clip", True),
        "duplicate_arrangement_clip": ("_duplicate_arrangement_clip", True),
        "get_arrangement_clip_notes": ("_get_arrangement_clip_notes", False),
        "set_arrangement_clip_notes": ("_set_arrangement_clip_notes", True),
        "set_song_time": ("_set_song_time", True),
        "get_arrangement_loop": ("_get_arrangement_loop", False),
        "set_arrangement_loop": ("_set_arrangement_loop", True),
        "back_to_arranger": ("_back_to_arranger", True),
        "duplicate_session_to_arrangement": (
            "_duplicate_session_to_arrangement",
            True,
        ),
        "session_to_arrangement": ("_session_to_arrangement", True),
    }

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self._command_queue = queue.Queue()
        self._response_queues = {}
        self._server_socket = None
        self._running = False
        self._start_server()
        self.log_message("AbletonMCP: Listening on port %d" % PORT)

    def disconnect(self):
        self._running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
        ControlSurface.disconnect(self)
        self.log_message("AbletonMCP: Disconnected")

    # ── Socket Server ───────────────────────────────────────────────

    def _start_server(self):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )
        self._server_socket.settimeout(1.0)
        self._server_socket.bind((HOST, PORT))
        self._server_socket.listen(5)
        self._running = True
        t = threading.Thread(target=self._accept_loop)
        t.daemon = True
        t.start()

    def _accept_loop(self):
        while self._running:
            try:
                client_sock, addr = self._server_socket.accept()
                self.log_message("AbletonMCP: Client connected from %s" % str(addr))
                t = threading.Thread(
                    target=self._handle_client, args=(client_sock,)
                )
                t.daemon = True
                t.start()
            except socket.timeout:
                continue
            except Exception:
                if self._running:
                    self.log_message(
                        "AbletonMCP: Accept error: %s" % traceback.format_exc()
                    )

    def _handle_client(self, client_sock):
        buffer = ""
        try:
            client_sock.settimeout(None)
            while self._running:
                data = client_sock.recv(8192)
                if not data:
                    break
                buffer += data.decode("utf-8")
                try:
                    command = json.loads(buffer)
                    buffer = ""
                    response = self._dispatch_command(command)
                    response_bytes = json.dumps(response).encode("utf-8")
                    client_sock.sendall(response_bytes)
                except ValueError:
                    # Incomplete JSON, keep buffering
                    continue
        except Exception:
            self.log_message(
                "AbletonMCP: Client error: %s" % traceback.format_exc()
            )
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

    # ── Command Dispatch ────────────────────────────────────────────

    def _dispatch_command(self, command):
        command_type = command.get("type", "")
        params = command.get("params", {})

        entry = self.COMMANDS.get(command_type)
        if entry is None:
            return {
                "status": "error",
                "message": "Unknown command: %s" % command_type,
            }

        method_name, needs_main_thread = entry
        handler = getattr(self, method_name)

        if not needs_main_thread:
            try:
                result = handler(**params) if params else handler()
                return {"status": "success", "result": result}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        # Schedule on main thread and wait for result
        response_q = queue.Queue()
        request_id = id(response_q)
        self._response_queues[request_id] = response_q

        def task():
            try:
                result = handler(**params) if params else handler()
                response_q.put({"status": "success", "result": result})
            except Exception as e:
                response_q.put({"status": "error", "message": str(e)})
            finally:
                self._response_queues.pop(request_id, None)

        self.schedule_message(0, task)

        try:
            return response_q.get(timeout=10.0)
        except queue.Empty:
            self._response_queues.pop(request_id, None)
            return {
                "status": "error",
                "message": "Timeout waiting for Ableton main thread",
            }

    # ── Helpers ─────────────────────────────────────────────────────

    def _get_track(self, track_index):
        tracks = self.song().tracks
        if track_index < 0 or track_index >= len(tracks):
            raise ValueError(
                "Track index %d out of range (0-%d)" % (track_index, len(tracks) - 1)
            )
        return tracks[track_index]

    def _get_clip_slot(self, track_index, clip_index):
        track = self._get_track(track_index)
        slots = track.clip_slots
        if clip_index < 0 or clip_index >= len(slots):
            raise ValueError(
                "Clip index %d out of range (0-%d)" % (clip_index, len(slots) - 1)
            )
        return slots[clip_index]

    def _get_clip(self, track_index, clip_index):
        slot = self._get_clip_slot(track_index, clip_index)
        if not slot.has_clip:
            raise ValueError(
                "No clip at track %d, slot %d" % (track_index, clip_index)
            )
        return slot.clip

    def _get_arrangement_clip(self, track_index, clip_index):
        track = self._get_track(track_index)
        clips = track.arrangement_clips
        if clip_index < 0 or clip_index >= len(clips):
            raise ValueError(
                "Arrangement clip index %d out of range (0-%d)"
                % (clip_index, len(clips) - 1)
            )
        return clips[clip_index]

    # ── Session / Info Handlers ─────────────────────────────────────

    def _get_session_info(self):
        song = self.song()
        return {
            "tempo": song.tempo,
            "signature_numerator": song.signature_numerator,
            "signature_denominator": song.signature_denominator,
            "track_count": len(song.tracks),
            "return_track_count": len(song.return_tracks),
            "scene_count": len(song.scenes),
            "is_playing": song.is_playing,
        }

    def _get_track_info(self, track_index):
        track = self._get_track(track_index)
        clip_slots = []
        for i, slot in enumerate(track.clip_slots):
            slot_info = {"index": i, "has_clip": slot.has_clip}
            if slot.has_clip:
                clip = slot.clip
                slot_info["clip_name"] = clip.name
                slot_info["clip_length"] = clip.length
                slot_info["is_playing"] = clip.is_playing
            clip_slots.append(slot_info)

        devices = []
        for i, device in enumerate(track.devices):
            devices.append({
                "index": i,
                "name": device.name,
                "class_name": device.class_name,
                "is_active": device.is_active,
            })

        return {
            "name": track.name,
            "mute": track.mute,
            "solo": track.solo,
            "arm": track.arm,
            "volume": track.mixer_device.volume.value,
            "pan": track.mixer_device.panning.value,
            "clip_slots": clip_slots,
            "devices": devices,
        }

    # ── Track Management Handlers ───────────────────────────────────

    def _create_midi_track(self, index=-1):
        song = self.song()
        if index == -1:
            index = len(song.tracks)
        song.create_midi_track(index)
        track = song.tracks[index]
        return {"index": index, "name": track.name}

    def _create_audio_track(self, index=-1):
        song = self.song()
        if index == -1:
            index = len(song.tracks)
        song.create_audio_track(index)
        track = song.tracks[index]
        return {"index": index, "name": track.name}

    def _delete_track(self, track_index):
        song = self.song()
        if track_index < 0 or track_index >= len(song.tracks):
            raise ValueError("Track index out of range")
        song.delete_track(track_index)
        return {"deleted": True}

    def _set_track_name(self, track_index, name):
        track = self._get_track(track_index)
        track.name = name
        return {"name": track.name}

    def _set_track_volume(self, track_index, volume):
        track = self._get_track(track_index)
        track.mixer_device.volume.value = max(0.0, min(1.0, float(volume)))
        return {"volume": track.mixer_device.volume.value}

    def _set_track_pan(self, track_index, pan):
        track = self._get_track(track_index)
        track.mixer_device.panning.value = max(-1.0, min(1.0, float(pan)))
        return {"pan": track.mixer_device.panning.value}

    def _set_track_mute(self, track_index, mute):
        track = self._get_track(track_index)
        track.mute = bool(mute)
        return {"mute": track.mute}

    def _set_track_solo(self, track_index, solo):
        track = self._get_track(track_index)
        track.solo = bool(solo)
        return {"solo": track.solo}

    # ── Clip Operation Handlers ─────────────────────────────────────

    def _create_clip(self, track_index, clip_index, length=4.0):
        slot = self._get_clip_slot(track_index, clip_index)
        if slot.has_clip:
            raise ValueError(
                "Clip slot at track %d, slot %d already has a clip"
                % (track_index, clip_index)
            )
        slot.create_clip(float(length))
        return {
            "track_index": track_index,
            "clip_index": clip_index,
            "length": float(length),
        }

    def _add_notes_to_clip(self, track_index, clip_index, notes):
        clip = self._get_clip(track_index, clip_index)
        note_tuples = []
        for n in notes:
            note_tuples.append((
                int(n.get("pitch", 60)),
                float(n.get("start_time", 0.0)),
                float(n.get("duration", 0.5)),
                int(n.get("velocity", 100)),
                bool(n.get("mute", False)),
            ))
        clip.select_all_notes()
        clip.replace_selected_notes(tuple(note_tuples))
        return {"notes_added": len(note_tuples)}

    def _set_clip_name(self, track_index, clip_index, name):
        clip = self._get_clip(track_index, clip_index)
        clip.name = name
        return {"name": clip.name}

    def _fire_clip(self, track_index, clip_index):
        slot = self._get_clip_slot(track_index, clip_index)
        slot.fire()
        return {"fired": True}

    def _stop_clip(self, track_index, clip_index):
        slot = self._get_clip_slot(track_index, clip_index)
        slot.stop()
        return {"stopped": True}

    # ── Transport Handlers ──────────────────────────────────────────

    def _start_playback(self):
        self.song().start_playing()
        return {"playing": True}

    def _stop_playback(self):
        self.song().stop_playing()
        return {"playing": False}

    def _set_tempo(self, tempo):
        tempo = max(20.0, min(999.0, float(tempo)))
        self.song().tempo = tempo
        return {"tempo": self.song().tempo}

    # ── Browser / Device Handlers ───────────────────────────────────

    def _get_browser_tree(self, category_type="all"):
        app = self.application()
        browser = app.browser

        category_map = {
            "instruments": [browser.instruments],
            "audio_effects": [browser.audio_effects],
            "midi_effects": [browser.midi_effects],
            "sounds": [browser.sounds],
            "drums": [browser.drums],
            "max_for_live": [browser.max_for_live],
        }

        if category_type == "all":
            sources = []
            for key in category_map:
                sources.extend(category_map[key])
        else:
            sources = category_map.get(category_type, [])
            if not sources:
                raise ValueError("Unknown category type: %s" % category_type)

        categories = []
        for source in sources:
            children = []
            for child in source.children:
                children.append({
                    "name": child.name,
                    "uri": child.uri if hasattr(child, "uri") else "",
                    "is_folder": child.is_folder if hasattr(child, "is_folder") else False,
                })
            categories.append({"name": source.name, "children": children})

        return {"categories": categories}

    def _get_browser_items_at_path(self, path):
        app = self.application()
        browser = app.browser
        parts = path.strip("/").split("/")

        # Start from top-level browser categories
        current_items = list(browser.instruments.children)
        current_items += list(browser.audio_effects.children)
        current_items += list(browser.midi_effects.children)
        current_items += list(browser.sounds.children)
        current_items += list(browser.drums.children)

        for part in parts:
            found = None
            for item in current_items:
                if item.name == part:
                    found = item
                    break
            if found is None:
                raise ValueError("Browser path not found: %s" % path)
            if hasattr(found, "children"):
                current_items = list(found.children)
            else:
                return {
                    "items": [{
                        "name": found.name,
                        "uri": found.uri if hasattr(found, "uri") else "",
                        "is_loadable": not (
                            found.is_folder if hasattr(found, "is_folder") else False
                        ),
                    }]
                }

        items = []
        for item in current_items:
            items.append({
                "name": item.name,
                "uri": item.uri if hasattr(item, "uri") else "",
                "is_folder": item.is_folder if hasattr(item, "is_folder") else False,
            })
        return {"items": items}

    def _load_browser_item(self, track_index, uri):
        app = self.application()
        browser = app.browser

        item = self._find_browser_item_by_uri(browser, uri)
        if item is None:
            raise ValueError("Browser item not found for URI: %s" % uri)

        track = self._get_track(track_index)
        self.song().view.selected_track = track
        browser.load_item(item)
        return {"loaded": True, "track_index": track_index, "uri": uri}

    def _find_browser_item_by_uri(self, browser, uri, max_depth=10):
        sources = [
            browser.instruments,
            browser.audio_effects,
            browser.midi_effects,
            browser.sounds,
            browser.drums,
        ]
        if hasattr(browser, "max_for_live"):
            sources.append(browser.max_for_live)

        for source in sources:
            result = self._search_uri(source, uri, max_depth)
            if result is not None:
                return result
        return None

    def _search_uri(self, item, uri, depth):
        if depth <= 0:
            return None
        if hasattr(item, "uri") and item.uri == uri:
            return item
        if hasattr(item, "children"):
            for child in item.children:
                result = self._search_uri(child, uri, depth - 1)
                if result is not None:
                    return result
        return None

    # ── Arrangement View Handlers ───────────────────────────────────

    def _get_arrangement_clips(self, track_index):
        track = self._get_track(track_index)
        clips = []
        for i, clip in enumerate(track.arrangement_clips):
            clips.append({
                "index": i,
                "name": clip.name,
                "start_time": clip.start_time,
                "end_time": clip.end_time,
                "length": clip.length,
                "is_playing": clip.is_playing,
            })
        return {"clips": clips}

    def _create_arrangement_clip(self, track_index, start_time, length):
        track = self._get_track(track_index)
        track.create_midi_clip(float(start_time), float(length))
        return {
            "track_index": track_index,
            "start_time": float(start_time),
            "length": float(length),
        }

    def _delete_arrangement_clip(self, track_index, clip_index):
        clip = self._get_arrangement_clip(track_index, clip_index)
        track = self._get_track(track_index)
        track.delete_clip(clip)
        return {"deleted": True}

    def _duplicate_arrangement_clip(
        self, track_index, clip_index, destination_time
    ):
        clip = self._get_arrangement_clip(track_index, clip_index)
        track = self._get_track(track_index)
        track.duplicate_clip_to_arrangement(clip, float(destination_time))
        return {
            "duplicated": True,
            "destination_time": float(destination_time),
        }

    def _get_arrangement_clip_notes(self, track_index, clip_index):
        clip = self._get_arrangement_clip(track_index, clip_index)
        notes = []
        if hasattr(clip, "get_notes_extended"):
            raw = clip.get_notes_extended(0, 128, 0.0, clip.length)
            for note in raw:
                notes.append({
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity,
                    "mute": note.mute,
                })
        else:
            raw = clip.get_notes(0.0, 0, clip.length, 128)
            for note in raw:
                notes.append({
                    "pitch": note[0],
                    "start_time": note[1],
                    "duration": note[2],
                    "velocity": note[3],
                    "mute": note[4],
                })
        return {"notes": notes}

    def _set_arrangement_clip_notes(self, track_index, clip_index, notes):
        clip = self._get_arrangement_clip(track_index, clip_index)
        note_tuples = []
        for n in notes:
            note_tuples.append((
                int(n.get("pitch", 60)),
                float(n.get("start_time", 0.0)),
                float(n.get("duration", 0.5)),
                int(n.get("velocity", 100)),
                bool(n.get("mute", False)),
            ))
        clip.select_all_notes()
        clip.replace_selected_notes(tuple(note_tuples))
        return {"notes_set": len(note_tuples)}

    def _set_song_time(self, time):
        self.song().current_song_time = max(0.0, float(time))
        return {"current_song_time": self.song().current_song_time}

    def _get_arrangement_loop(self):
        song = self.song()
        return {
            "loop_start": song.loop_start,
            "loop_length": song.loop_length,
        }

    def _set_arrangement_loop(self, start, length):
        song = self.song()
        song.loop_start = max(0.0, float(start))
        song.loop_length = max(0.0, float(length))
        return {
            "loop_start": song.loop_start,
            "loop_length": song.loop_length,
        }

    def _back_to_arranger(self):
        self.song().back_to_arranger = True
        return {"back_to_arranger": True}

    def _duplicate_session_to_arrangement(
        self, track_index, clip_index, destination_time
    ):
        clip = self._get_clip(track_index, clip_index)
        track = self._get_track(track_index)
        track.duplicate_clip_to_arrangement(clip, float(destination_time))
        return {
            "duplicated": True,
            "track_index": track_index,
            "clip_index": clip_index,
            "destination_time": float(destination_time),
        }

    def _session_to_arrangement(self, scene_indices):
        song = self.song()
        current_time = 0.0
        clips_placed = 0

        for scene_idx in scene_indices:
            if scene_idx < 0 or scene_idx >= len(song.scenes):
                raise ValueError(
                    "Scene index %d out of range (0-%d)"
                    % (scene_idx, len(song.scenes) - 1)
                )

            # Find the longest clip in this scene to determine scene length
            scene_length = 0.0
            scene_clips = []
            for track_idx, track in enumerate(song.tracks):
                slots = track.clip_slots
                if scene_idx < len(slots) and slots[scene_idx].has_clip:
                    clip = slots[scene_idx].clip
                    scene_clips.append((track, clip))
                    if clip.length > scene_length:
                        scene_length = clip.length

            if scene_length == 0.0:
                continue

            # Duplicate each clip in the scene to the arrangement
            for track, clip in scene_clips:
                track.duplicate_clip_to_arrangement(clip, current_time)
                clips_placed += 1

            current_time += scene_length

        # Switch to arrangement playback
        song.back_to_arranger = True

        return {
            "clips_placed": clips_placed,
            "total_length": current_time,
            "scenes_processed": len(scene_indices),
        }
