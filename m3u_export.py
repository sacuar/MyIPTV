"""Helpers for exporting playlists in the standard extended M3U format."""

import os
from pathlib import Path
import tempfile


def _safe_text(value):
    return str(value or "").replace("\r", " ").replace("\n", " ").strip()


def _attribute(name, value):
    value = _safe_text(value)
    if not value:
        return ""
    return f' {name}="{value.replace(chr(34), "&quot;")}"'


def serialize_m3u(streams):
    """Export IPTV channel metadata and UTF-8 names without directive injection."""
    lines = ["#EXTM3U"]
    for stream in streams:
        url = str(stream.get("url") or "").strip()
        if not url or "\r" in url or "\n" in url or url.startswith("#"):
            continue

        tvg = stream.get("tvg") or {}
        if not isinstance(tvg, dict):
            tvg = {}
        meta = "#EXTINF:-1"
        for key in ("id", "name", "url", "chno"):
            meta += _attribute("tvg-" + key, tvg.get(key))
        meta += _attribute("tvg-logo", stream.get("logo"))
        meta += _attribute("group-title", stream.get("category"))
        for field, key in (("country", "code"), ("language", "name")):
            data = stream.get(field)
            if isinstance(data, dict):
                meta += _attribute("tvg-" + field, data.get(key))
        name = _safe_text(stream.get("name")) or "Untitled channel"
        lines.extend((f"{meta},{name}", url))

    return "\n".join(lines) + "\n"


def save_m3u(destination, streams):
    """Atomically replace the selected file, avoiding partially written playlists."""
    target = Path(destination)
    content = serialize_m3u(streams)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", delete=False,
            dir=target.parent, prefix=".bang-iptv-", suffix=".tmp",
        ) as file:
            temp_path = Path(file.name)
            file.write(content)
        os.replace(temp_path, target)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return target
