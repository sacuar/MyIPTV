"""Playlist loading, selection and export, separate from the Tk interface."""

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


@dataclass(frozen=True)
class PlaylistResult:
    channels: list
    checked: bool

    @property
    def counts(self):
        return Counter(channel_status(channel, self.checked) for channel in self.channels)

    @property
    def duplicates(self):
        urls = [c.get("url") for c in self.channels if c.get("url")]
        return len(urls) - len(set(urls))


def validate_source(value):
    """Accept an existing local playlist or HTTP(S) URL only."""
    source = str(value).strip().strip('"')
    if not source:
        raise ValueError("Enter a playlist URL or select a local M3U file.")

    url = urlsplit(source)
    if url.scheme in ("http", "https"):
        if not url.netloc:
            raise ValueError("The playlist URL has no host.")
        return source
    if "://" in source:
        raise ValueError("Only HTTP/HTTPS URLs or local files are supported.")

    path = Path(source).expanduser()
    if not path.is_file():
        raise ValueError("The selected playlist file does not exist.")
    return str(path)


def load_playlist(source, *, check_live=True, timeout=7, parser_factory=None):
    """Run on a worker thread: the third-party parser performs network checks."""
    source = validate_source(source)
    if parser_factory is None:
        from m3u_parser import M3uParser
        parser_factory = M3uParser

    parser = parser_factory(timeout=timeout)
    parser.parse_m3u(source, check_live=check_live)
    channels = [dict(row) for row in parser.get_list() if isinstance(row, dict) and row.get("url")]
    return PlaylistResult(channels=channels, checked=check_live)


def channel_status(channel, checked):
    if not checked:
        return "UNCHECKED"
    status = str(channel.get("status") or "").upper()
    return status if status in ("GOOD", "BAD") else "UNKNOWN"


def select_channels(result, *, status="All", category="All", query=""):
    query = query.strip().casefold()
    output = []
    for channel in result.channels:
        if status != "All" and channel_status(channel, result.checked) != status:
            continue
        if category != "All" and str(channel.get("category") or "Other") != category:
            continue
        if query and query not in str(channel.get("name") or "").casefold():
            continue
        output.append(channel)
    return output


def export_channels(result, *, only_working=True, deduplicate=True):
    """By default export validated working links only, without duplicates."""
    if only_working and not result.checked:
        raise ValueError("Validate links before exporting working channels only.")
    chosen = []
    seen = set()
    for channel in result.channels:
        if only_working and channel_status(channel, True) != "GOOD":
            continue
        url = channel.get("url")
        if deduplicate and url in seen:
            continue
        if url:
            seen.add(url)
            chosen.append(channel)
    return chosen
