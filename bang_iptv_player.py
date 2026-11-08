"""BANG IPTV Pro — Windows desktop player.

Run with: python bang_iptv_player.py
Requires: python-vlc and a desktop installation of VLC Media Player.
"""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import sys
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from player_core import FREE_PLAYLISTS, filtered_channels, load_channels
from health_engine import (
    BATCH_SIZE, MAX_WORKERS, CheckResult, HealthMonitor, check_stream, hidden_status,
)
from m3u_export import save_m3u


BG = "#10151f"
PANEL = "#1b2431"
TEXT = "#f1f5f9"
MUTED = "#9baaba"
ACCENT = "#9ab46b"
VLC_DLL_HANDLE = None


def config_file():
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home()))
        return root / "BANGIPTVPro" / "settings.json"
    return Path.home() / ".config" / "bang-iptv-pro" / "settings.json"


def read_settings():
    try:
        data = json.loads(config_file().read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return data
    except (OSError, ValueError, TypeError):
        return {}


def write_settings(data):
    target = config_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=target.parent,
            prefix=".settings-", suffix=".tmp", delete=False,
        ) as output:
            temp_name = output.name
            json.dump(data, output, ensure_ascii=False, indent=2)
        os.replace(temp_name, target)
    finally:
        if temp_name:
            Path(temp_name).unlink(missing_ok=True)


def initialize_vlc():
    """Find an installed Windows VLC without bundling copyrighted VLC binaries."""
    global VLC_DLL_HANDLE
    if os.name == "nt":
        candidates = [
            Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "VideoLAN" / "VLC",
            Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")) / "VideoLAN" / "VLC",
        ]
        for directory in candidates:
            dll = directory / "libvlc.dll"
            if dll.is_file():
                os.environ["PYTHON_VLC_LIB_PATH"] = str(dll)
                os.environ["PYTHON_VLC_MODULE_PATH"] = str(directory / "plugins")
                if hasattr(os, "add_dll_directory"):
                    VLC_DLL_HANDLE = os.add_dll_directory(str(directory))
                break

    try:
        import vlc
        return vlc
    except (OSError, ImportError) as exc:
        raise RuntimeError(
            "VLC playback is unavailable. Install VLC Media Player and "
            "the python-vlc package, then restart BANG IPTV Pro."
        ) from exc


class VLCController:
    def __init__(self, surface):
        self.vlc = initialize_vlc()
        self.instance = self.vlc.Instance("--quiet", "--no-video-title-show")
        if self.instance is None:
            raise RuntimeError("VLC could not start. Check your VLC installation.")
        self.player = self.instance.media_player_new()
        surface.update_idletasks()
        window_id = surface.winfo_id()
        if sys.platform == "win32":
            self.player.set_hwnd(window_id)
        elif sys.platform == "darwin":
            self.player.set_nsobject(window_id)
        else:
            self.player.set_xwindow(window_id)

    def play(self, url):
        media = self.instance.media_new(url)
        media.add_option(":network-caching=1500")
        media.add_option(":live-caching=1500")
        self.player.set_media(media)
        media.release()
        result = self.player.play()
        if result == -1:
            raise RuntimeError("VLC could not open this channel.")

    def stop(self):
        self.player.stop()

    def close(self):
        self.player.stop()
        self.player.release()
        self.instance.release()


class BANGIPTVPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BANG IPTV Pro")
        self.geometry("1210x730")
        self.minsize(860, 530)
        self.configure(background=BG)

        settings = read_settings()
        self.favorites = set(v for v in settings.get("favorites", []) if isinstance(v, str))
        self.channels = []
        self.visible = []
        self.backend = None
        self.current = None
        self.busy = False
        self.request_id = 0
        self.render_token = 0
        self.search_job = None
        self.messages = queue.Queue()
        self.fullscreen = False
        self.volume = tk.DoubleVar(value=max(0, min(100, int(settings.get("volume", 70)))))
        self.source_kind = tk.StringVar(value="Bangladesh — Free TV")
        self.source = tk.StringVar(value=FREE_PLAYLISTS["Bangladesh — Free TV"])
        self.search = tk.StringVar()
        self.group = tk.StringVar(value="All")
        self.only_favorites = tk.BooleanVar(value=False)
        self.health = HealthMonitor()
        self.health_generation = 0
        self.health_busy = False
        self.loaded_source = ""
        self.last_refresh = 0.0
        self.auto_check = tk.BooleanVar(value=settings.get("auto_check", True))
        self.auto_refresh = tk.BooleanVar(value=settings.get("auto_refresh", True))
        self.hide_unavailable = tk.BooleanVar(value=settings.get("hide_unavailable", True))
        self.health_summary = tk.StringVar(value="Stream health: unchecked. Background checking starts after loading.")
        self.failed_playback_url = None
        self.playing_reported_url = None
        self.status = tk.StringVar(value="Load a playlist to start watching.")
        self.now_playing = tk.StringVar(value="No channel selected")

        self._build_ui()
        self.search.trace_add("write", self._delay_filter)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(100, self._drain_messages)
        self.after(1400, self._monitor_playback)
        self.after(15000, self._health_tick)
        self.after(60000, self._refresh_tick)

        self.bind("<Control-f>", lambda _event: self.search_entry.focus_set())
        self.bind("<Control-o>", lambda _event: self.choose_file())
        self.bind("<Escape>", lambda _event: self.toggle_fullscreen(force_off=True))
        self.bind("<F11>", lambda _event: self.toggle_fullscreen())
        self.bind("<space>", self._space_key)
        self.bind("<KeyPress-m>", self._mute_key)

    def _build_ui(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TFrame", background=PANEL)
        style.configure("TLabel", background=PANEL, foreground=TEXT)
        style.configure("TButton", padding=(10, 6))
        style.configure("Treeview", background=PANEL, foreground=TEXT,
                        fieldbackground=PANEL, rowheight=29)
        style.map("Treeview", background=[("selected", "#3d5341")])
        style.configure("Treeview.Heading", background="#283545", foreground=TEXT)
        style.configure("TCheckbutton", background=PANEL, foreground=TEXT)
        style.configure("TCombobox", padding=5)

        self.sidebar = ttk.Frame(self, padding=16, width=410)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="BANG IPTV Pro", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(self.sidebar, text="Free TV · Your playlists · VLC playback",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 18))

        ttk.Label(self.sidebar, text="Playlist").pack(anchor="w")
        kinds = list(FREE_PLAYLISTS) + ["Custom URL / file"]
        picker = ttk.Combobox(self.sidebar, textvariable=self.source_kind,
                              values=kinds, state="readonly")
        picker.pack(fill="x", pady=(4, 7))
        picker.bind("<<ComboboxSelected>>", self.select_preset)

        ttk.Entry(self.sidebar, textvariable=self.source).pack(fill="x", pady=(0, 7))
        source_buttons = ttk.Frame(self.sidebar)
        source_buttons.pack(fill="x", pady=(0, 15))
        ttk.Button(source_buttons, text="Browse…", command=self.choose_file).pack(side="left")
        self.load_button = ttk.Button(source_buttons, text="Load channels", command=self.load)
        self.load_button.pack(side="right")
        ttk.Button(source_buttons, text="Refresh", command=self.refresh_playlist).pack(side="right", padx=(0, 8))

        health_controls = ttk.Frame(self.sidebar)
        health_controls.pack(fill="x", pady=(0, 8))
        ttk.Checkbutton(health_controls, text="Auto-check links", variable=self.auto_check,
                        command=self._save_settings).pack(side="left")
        ttk.Checkbutton(health_controls, text="Auto-refresh list", variable=self.auto_refresh,
                        command=self._save_settings).pack(side="right")

        health_actions = ttk.Frame(self.sidebar)
        health_actions.pack(fill="x", pady=(0, 10))
        ttk.Checkbutton(health_actions, text="Hide stopped", variable=self.hide_unavailable,
                        command=self._health_visibility_change).pack(side="left")
        ttk.Button(health_actions, text="Check now", command=lambda: self._start_health(force=True)).pack(side="right")

        ttk.Label(self.sidebar, text="Search channels").pack(anchor="w")
        self.search_entry = ttk.Entry(self.sidebar, textvariable=self.search)
        self.search_entry.pack(fill="x", pady=(4, 8))

        filters = ttk.Frame(self.sidebar)
        filters.pack(fill="x", pady=(0, 9))
        self.groups = ttk.Combobox(filters, textvariable=self.group,
                                   state="readonly", values=["All"], width=20)
        self.groups.pack(side="left", fill="x", expand=True)
        self.groups.bind("<<ComboboxSelected>>", lambda _event: self.render())
        ttk.Checkbutton(filters, text="★ Favourites", variable=self.only_favorites,
                        command=self.render).pack(side="right", padx=(10, 0))

        channel_frame = ttk.Frame(self.sidebar)
        channel_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(channel_frame, columns=("fav", "name", "group", "health"),
                                 show="headings", selectmode="browse")
        self.tree.heading("fav", text="★")
        self.tree.heading("name", text="Channel")
        self.tree.heading("group", text="Group")
        self.tree.heading("health", text="Health")
        self.tree.column("fav", width=32, stretch=False, anchor="center")
        self.tree.column("name", width=200, minwidth=100)
        self.tree.column("group", width=90, minwidth=60)
        self.tree.column("health", width=74, stretch=False, anchor="center")
        scroll = ttk.Scrollbar(channel_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda _event: self.play_selected())
        self.tree.bind("<Return>", lambda _event: self.play_selected())

        sidebar_actions = ttk.Frame(self.sidebar)
        sidebar_actions.pack(fill="x", pady=(10, 0))
        ttk.Button(sidebar_actions, text="▶ Watch", command=self.play_selected).pack(side="left")
        ttk.Button(sidebar_actions, text="★ Add / remove favourite",
                   command=self.toggle_favorite).pack(side="right")
        ttk.Button(self.sidebar, text="Save verified working channels as M3U…",
                   command=self.export_working).pack(fill="x", pady=(8, 0))
        ttk.Label(self.sidebar, textvariable=self.health_summary,
                  wraplength=370, foreground=ACCENT).pack(fill="x", pady=(8, 0))

        self.video_column = ttk.Frame(self, padding=(10, 16, 16, 16))
        self.video_column.pack(side="right", fill="both", expand=True)
        tk.Label(self.video_column, textvariable=self.now_playing, anchor="w",
                 bg=PANEL, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(fill="x", pady=(0, 10))

        self.surface = tk.Frame(self.video_column, background="#000000", highlightthickness=0)
        self.surface.pack(fill="both", expand=True)

        controls = ttk.Frame(self.video_column)
        controls.pack(fill="x", pady=(12, 8))
        ttk.Button(controls, text="▶ / ⏸", command=self.play_pause).pack(side="left")
        ttk.Button(controls, text="■ Stop", command=self.stop).pack(side="left", padx=(8, 0))
        ttk.Button(controls, text="⛶ Fullscreen (F11)", command=self.toggle_fullscreen).pack(side="left", padx=(8, 0))
        ttk.Label(controls, text="Volume").pack(side="left", padx=(16, 4))
        ttk.Scale(controls, from_=0, to=100, orient="horizontal", variable=self.volume,
                  command=self.set_volume).pack(side="left", fill="x", expand=True)

        tk.Label(self.video_column, textvariable=self.status, bg=PANEL, fg=MUTED,
                 anchor="w", wraplength=650).pack(fill="x")

    def select_preset(self, _event=None):
        self.source.set(FREE_PLAYLISTS.get(self.source_kind.get(), ""))

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[
            ("M3U playlists", "*.m3u *.m3u8 *.txt"), ("All files", "*.*"),
        ])
        if path:
            self.source_kind.set("Custom URL / file")
            self.source.set(path)

    def refresh_playlist(self):
        if not self.loaded_source:
            self.load()
        else:
            self.load(refresh=True)

    def load(self, refresh=False):
        if self.busy:
            return
        source = self.loaded_source if refresh else self.source.get().strip()
        if not source:
            messagebox.showwarning("Playlist", "Choose a playlist first.")
            return
        self.busy = True
        self.load_button.configure(state="disabled")
        self.status.set("Refreshing playlist from its source…" if refresh else "Loading channels…")
        self.request_id += 1
        request_id = self.request_id

        def worker():
            try:
                channels = load_channels(source)
                self.messages.put(("playlist", request_id, channels, None, source))
            except Exception as error:
                self.messages.put(("playlist", request_id, None, str(error), source))

        threading.Thread(target=worker, daemon=True).start()

    def _drain_messages(self):
        needs_render = False
        try:
            while True:
                event = self.messages.get_nowait()
                if event[0] == "playlist":
                    _, request_id, channels, error, source = event
                    if request_id != self.request_id:
                        continue
                    self.busy = False
                    self.load_button.configure(state="normal")
                    if error:
                        self.status.set("Playlist refresh failed; existing channels retained.")
                        messagebox.showerror("Playlist loading failed", error)
                        continue
                    source_changed = source != self.loaded_source
                    self.loaded_source = source
                    self.last_refresh = time.monotonic()
                    self.channels = channels
                    self.group.set("All" if source_changed else
                                   self.group.get() if self.group.get() in
                                   {c.group for c in channels} else "All")
                    self.groups.configure(values=["All"] + sorted({c.group for c in channels}))
                    if source_changed:
                        self.health = HealthMonitor()
                    self.health_generation += 1
                    self.health_busy = False
                    self.status.set(f"{len(channels):,} unique channels loaded. Auto-checking is " +
                                    ("enabled." if self.auto_check.get() else "disabled."))
                    needs_render = True
                    if self.auto_check.get():
                        self.after(500, self._start_health)
                elif event[0] == "health":
                    _, generation, url, result = event
                    if generation != self.health_generation:
                        continue
                    self.health.record(url, result)
                    needs_render = True
                elif event[0] == "health_done":
                    _, generation = event
                    if generation == self.health_generation:
                        self.health_busy = False
                        needs_render = True
        except queue.Empty:
            pass
        if needs_render:
            self.render()
        self.after(100, self._drain_messages)

    def _health_visibility_change(self):
        self._save_settings()
        self.render()

    def _start_health(self, force=False):
        if self.health_busy or self.busy or not self.channels:
            return
        preferred = [c.url for c in self.visible]
        urls = self.health.choose(self.channels, preferred=preferred,
                                  limit=BATCH_SIZE, force=force)
        if not urls:
            self._update_health_summary()
            return
        self.health_busy = True
        generation = self.health_generation
        self._update_health_summary()

        def worker():
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                tasks = {executor.submit(check_stream, url): url for url in urls}
                for future in as_completed(tasks):
                    url = tasks[future]
                    try:
                        result = future.result()
                    except Exception:
                        result = CheckResult("unknown", "Unexpected validation error.")
                    self.messages.put(("health", generation, url, result))
            self.messages.put(("health_done", generation))

        threading.Thread(target=worker, daemon=True).start()

    def _health_tick(self):
        if self.auto_check.get():
            self._start_health()
        self.after(15000, self._health_tick)

    def _refresh_tick(self):
        if (self.auto_refresh.get() and self.loaded_source and
                time.monotonic() - self.last_refresh >= 1800 and not self.busy):
            self.load(refresh=True)
        self.after(60000, self._refresh_tick)

    def _update_health_summary(self):
        summary = self.health.counts(self.channels)
        hidden = sum(hidden_status(self.health.status(c.url)) for c in self.channels)
        self.health_summary.set(
            f"{len(self.visible):,} shown / {len(self.channels):,} channels · "
            f"{summary['online']:,} online · {hidden:,} stopped · "
            f"{summary['blocked']:,} restricted · {summary['unchecked']:,} unchecked" +
            (" · Checking…" if self.health_busy else "")
        )

    def export_working(self):
        verified = [c for c in self.channels if self.health.status(c.url) == "online"]
        if not verified:
            messagebox.showinfo("Export", "No channels verified online yet. Use Check now first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save verified channels", defaultextension=".m3u",
            initialfile="BANG_IPTV_verified.m3u",
            filetypes=[("M3U playlist", "*.m3u")],
        )
        if not path:
            return
        streams = [{
            "name": c.name, "url": c.url, "logo": c.logo, "category": c.group,
            "tvg": {"id": c.tvg_id},
        } for c in verified]
        try:
            save_m3u(path, streams)
        except OSError as error:
            messagebox.showerror("Export failed", str(error))
            return
        messagebox.showinfo("Saved", f"Exported {len(verified):,} verified channels. "
                            "Unverified and stopped channels were not included.")

    def _delay_filter(self, *_args):
        if self.search_job is not None:
            self.after_cancel(self.search_job)
        self.search_job = self.after(150, self.render)

    def render(self):
        self.search_job = None
        self.render_token += 1
        token = self.render_token
        self.visible = filtered_channels(
            self.channels, query=self.search.get(), group=self.group.get(),
            favorites=self.favorites if self.only_favorites.get() else None,
        )
        if self.hide_unavailable.get():
            self.visible = [c for c in self.visible
                            if not hidden_status(self.health.status(c.url))]
        self._update_health_summary()
        items = self.tree.get_children()
        if items:
            self.tree.delete(*items)
        self._add_rows(token, 0)

    def _add_rows(self, token, start):
        if token != self.render_token:
            return
        for index in range(start, min(start + 150, len(self.visible))):
            item = self.visible[index]
            self.tree.insert("", "end", iid=str(index), values=(
                "★" if item.url in self.favorites else "", item.name, item.group,
                self.health.status(item.url),
            ))
        if start + 150 < len(self.visible):
            self.after(1, self._add_rows, token, start + 150)

    def _selected_channel(self):
        selected = self.tree.selection()
        if not selected:
            return None
        index = int(selected[0])
        return self.visible[index] if 0 <= index < len(self.visible) else None

    def play_selected(self):
        channel = self._selected_channel()
        if channel is None:
            messagebox.showinfo("Select a channel", "Select a channel to play.")
            return
        self.play_channel(channel)

    def play_channel(self, channel):
        try:
            if self.backend is None:
                self.backend = VLCController(self.surface)
                self.backend.player.audio_set_volume(int(self.volume.get()))
            self.failed_playback_url = None
            self.playing_reported_url = None
            self.backend.play(channel.url)
        except Exception as error:
            self.status.set("Playback is unavailable.")
            messagebox.showerror("Cannot play channel", str(error))
            return
        self.current = channel
        self.now_playing.set(channel.name)
        self.status.set(f"Connecting to {channel.name}…")

    def play_pause(self):
        if self.backend is None or self.current is None:
            self.play_selected()
            return
        if self.backend.player.is_playing():
            self.backend.player.set_pause(1)
            self.status.set("Paused")
        else:
            self.backend.player.play()
            self.status.set("Playing / buffering…")

    def stop(self):
        if self.backend:
            self.backend.stop()
        self.current = None
        self.now_playing.set("No channel selected")
        self.status.set("Stopped")

    def set_volume(self, _value=None):
        if self.backend:
            self.backend.player.audio_set_volume(int(self.volume.get()))

    def toggle_favorite(self):
        channel = self._selected_channel()
        if channel is None:
            return
        if channel.url in self.favorites:
            self.favorites.remove(channel.url)
        else:
            self.favorites.add(channel.url)
        self._save_settings()
        self.render()

    def _save_settings(self):
        try:
            write_settings({
                "favorites": sorted(self.favorites),
                "volume": int(self.volume.get()),
                "auto_check": self.auto_check.get(),
                "auto_refresh": self.auto_refresh.get(),
                "hide_unavailable": self.hide_unavailable.get(),
            })
        except OSError:
            self.status.set("Preferences could not be saved.")

    def toggle_fullscreen(self, force_off=False):
        new_state = False if force_off else not self.fullscreen
        if new_state == self.fullscreen:
            return
        self.fullscreen = new_state
        if new_state:
            self.sidebar.pack_forget()
            self.attributes("-fullscreen", True)
        else:
            self.attributes("-fullscreen", False)
            self.sidebar.pack(side="left", fill="y", before=self.video_column)

    def _space_key(self, _event):
        if isinstance(self.focus_get(), (ttk.Entry, tk.Entry)):
            return
        self.play_pause()
        return "break"

    def _mute_key(self, _event):
        if isinstance(self.focus_get(), (ttk.Entry, tk.Entry)):
            return
        if self.backend:
            self.backend.player.audio_toggle_mute()

    def _monitor_playback(self):
        if self.backend and self.current:
            try:
                state = self.backend.player.get_state()
                if state == self.backend.vlc.State.Error:
                    if self.failed_playback_url != self.current.url:
                        self.failed_playback_url = self.current.url
                        self.health.record(
                            self.current.url, CheckResult("playback_failed", "VLC failed to play stream.")
                        )
                        self.render()
                    self.status.set("Stream failed and is hidden from the channel list. "
                                    "Untick Hide stopped to see it.")
                elif state == self.backend.vlc.State.Playing:
                    if self.playing_reported_url != self.current.url:
                        self.playing_reported_url = self.current.url
                        self.health.record(self.current.url,
                                           CheckResult("online", "Playback confirmed by VLC."))
                        self.render()
                    self.status.set(f"Playing: {self.current.name}")
                elif state == self.backend.vlc.State.Buffering:
                    self.status.set("Buffering…")
            except (OSError, AttributeError):
                pass
        self.after(1400, self._monitor_playback)

    def close(self):
        self._save_settings()
        if self.backend:
            self.backend.close()
        self.destroy()


if __name__ == "__main__":
    BANGIPTVPlayer().mainloop()
