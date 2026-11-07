"""BANG IPTV Pro playlist checking utility.

Run `python gui2.py`. The released Windows IPTV player is a separate binary.
"""

import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from m3u_export import save_m3u
from playlist_service import (
    channel_status, export_channels, load_playlist, select_channels, validate_source,
)


class PlaylistApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BANG IPTV Pro | Playlist Tools")
        self.geometry("1020x620")
        self.minsize(760, 460)
        self.source = tk.StringVar()
        self.search = tk.StringVar()
        self.category = tk.StringVar(value="All")
        self.status = tk.StringVar(value="All")
        self.check_live = tk.BooleanVar(value=True)
        self.only_working = tk.BooleanVar(value=True)
        self.deduplicate = tk.BooleanVar(value=True)
        self.summary = tk.StringVar(value="Select an M3U file or paste a playlist URL.")
        self.results = None
        self.messages = queue.Queue()
        self.busy = False
        self.render_token = 0
        self.search_after = None

        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Treeview", rowheight=26)
        style.configure("Heading.TLabel", font=("Segoe UI", 16, "bold"))

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="BANG IPTV Pro · Playlist Validator", style="Heading.TLabel").pack(anchor="w")

        source_bar = ttk.Frame(frame)
        source_bar.pack(fill="x", pady=(14, 8))
        ttk.Entry(source_bar, textvariable=self.source).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(source_bar, text="Browse…", command=self.browse).pack(side="left", padx=(0, 8))
        self.load_button = ttk.Button(source_bar, text="Load / Validate", command=self.load)
        self.load_button.pack(side="left")

        options = ttk.Frame(frame)
        options.pack(fill="x", pady=(0, 8))
        ttk.Checkbutton(options, text="Check live streams", variable=self.check_live).pack(side="left")
        self.progress = ttk.Progressbar(options, mode="indeterminate", length=145)
        self.progress.pack(side="right")
        ttk.Label(frame, textvariable=self.summary).pack(anchor="w", pady=(0, 10))

        filters = ttk.Frame(frame)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Label(filters, text="Search").pack(side="left")
        ttk.Entry(filters, textvariable=self.search, width=28).pack(side="left", padx=(6, 14))
        ttk.Label(filters, text="Status").pack(side="left")
        self.status_box = ttk.Combobox(
            filters, textvariable=self.status, state="readonly", width=12,
            values=["All", "GOOD", "BAD", "UNKNOWN", "UNCHECKED"],
        )
        self.status_box.pack(side="left", padx=(6, 14))
        ttk.Label(filters, text="Category").pack(side="left")
        self.category_box = ttk.Combobox(
            filters, textvariable=self.category, state="readonly", width=23,
            values=["All"],
        )
        self.category_box.pack(side="left", padx=(6, 0))

        table = ttk.Frame(frame)
        table.pack(fill="both", expand=True)
        columns = ("name", "status", "category", "url")
        self.tree = ttk.Treeview(table, columns=columns, show="headings")
        for field, label, width in (
            ("name", "Channel", 220), ("status", "Status", 95),
            ("category", "Category", 165), ("url", "Stream URL", 450),
        ):
            self.tree.heading(field, text=label)
            self.tree.column(field, width=width, minwidth=70, stretch=field == "url")
        scroll_y = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        table.grid_rowconfigure(0, weight=1)
        table.grid_columnconfigure(0, weight=1)

        bottom = ttk.Frame(frame)
        bottom.pack(fill="x", pady=(12, 0))
        ttk.Checkbutton(bottom, text="Export working only", variable=self.only_working).pack(side="left")
        ttk.Checkbutton(bottom, text="Remove duplicate URLs", variable=self.deduplicate).pack(side="left", padx=(16, 0))
        self.save_button = ttk.Button(bottom, text="Export M3U…", command=self.save, state="disabled")
        self.save_button.pack(side="right")

        self.search.trace_add("write", self._schedule_render)
        self.status_box.bind("<<ComboboxSelected>>", lambda _event: self.render())
        self.category_box.bind("<<ComboboxSelected>>", lambda _event: self.render())

    def browse(self):
        path = filedialog.askopenfilename(
            title="Open IPTV playlist",
            filetypes=[("IPTV playlists", "*.m3u *.m3u8 *.txt"), ("All files", "*.*")],
        )
        if path:
            self.source.set(path)

    def load(self):
        if self.busy:
            return
        try:
            source = validate_source(self.source.get())
        except ValueError as exc:
            messagebox.showwarning("Playlist source", str(exc))
            return
        self.busy = True
        self.results = None
        self.summary.set("Loading playlist and checking stream availability…" if self.check_live.get() else "Loading playlist without checking streams…")
        self.load_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
        self.progress.start(12)
        self.render()
        threading.Thread(
            target=self._worker, args=(source, self.check_live.get()), daemon=True,
        ).start()
        self.after(100, self._check_messages)

    def _worker(self, source, check_live):
        try:
            result = load_playlist(source, check_live=check_live)
        except Exception as exc:
            self.messages.put(("error", exc))
        else:
            self.messages.put(("success", result))

    def _check_messages(self):
        try:
            kind, data = self.messages.get_nowait()
        except queue.Empty:
            if self.busy:
                self.after(100, self._check_messages)
            return

        self.busy = False
        self.progress.stop()
        self.load_button.configure(state="normal")
        if kind == "error":
            self.summary.set("Could not load the playlist. Check the source or internet connection.")
            messagebox.showerror("Playlist error", str(data))
            return

        self.results = data
        self.only_working.set(data.checked)
        counts = data.counts
        if data.checked:
            self.summary.set(
                f"{len(data.channels):,} channels · {counts['GOOD']:,} working · "
                f"{counts['BAD']:,} unavailable · {counts['UNKNOWN']:,} unknown · "
                f"{data.duplicates:,} duplicate URLs"
            )
        else:
            self.summary.set(f"{len(data.channels):,} channels · Not checked · {data.duplicates:,} duplicate URLs")
        self.category_box.configure(values=["All"] + sorted({
            str(ch.get("category") or "Other") for ch in data.channels
        }))
        self.category.set("All")
        self.status.set("All")
        self.save_button.configure(state="normal" if data.channels else "disabled")
        self.render()

    def _schedule_render(self, *_args):
        if self.search_after is not None:
            self.after_cancel(self.search_after)
        self.search_after = self.after(180, self.render)

    def render(self):
        self.search_after = None
        self.render_token += 1
        token = self.render_token
        self.tree.delete(*self.tree.get_children())
        if self.results is None:
            return
        matching = select_channels(
            self.results, status=self.status.get(), category=self.category.get(),
            query=self.search.get(),
        )
        self._append_rows(matching, token, 0)

    def _append_rows(self, rows, token, index):
        if token != self.render_token:
            return
        for channel in rows[index:index + 150]:
            self.tree.insert("", "end", values=(
                channel.get("name") or "Untitled channel",
                channel_status(channel, self.results.checked),
                channel.get("category") or "Other",
                channel.get("url") or "",
            ))
        if index + 150 < len(rows):
            self.after(1, self._append_rows, rows, token, index + 150)

    def save(self):
        if self.results is None or self.busy:
            return
        try:
            selected = export_channels(
                self.results, only_working=self.only_working.get(),
                deduplicate=self.deduplicate.get(),
            )
        except ValueError as exc:
            messagebox.showwarning("Export", str(exc))
            return
        if not selected:
            messagebox.showinfo("Export", "There are no channels matching the export options.")
            return
        destination = filedialog.asksaveasfilename(
            title="Export playlist", defaultextension=".m3u",
            filetypes=[("M3U playlists", "*.m3u"), ("All files", "*.*")],
            initialfile="bang_working_channels.m3u" if self.only_working.get() else "bang_channels.m3u",
        )
        if not destination:
            return
        try:
            save_m3u(destination, selected)
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))
            return
        messagebox.showinfo("Export complete", f"Saved {len(selected):,} channels to:\n{destination}")


if __name__ == "__main__":
    PlaylistApp().mainloop()
