"""Core playlist handling for the BANG IPTV Pro desktop player.

Uses only the Python standard library. No VLC or GUI dependency here.
"""

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import re


MAX_PLAYLIST_BYTES = 20 * 1024 * 1024
MAX_CHANNELS = 100_000
STREAM_SCHEMES = {"http", "https", "rtsp", "rtmp", "rtp", "udp"}

FREE_PLAYLISTS = {
    "Bangladesh — Free TV": "https://iptv-org.github.io/iptv/countries/bd.m3u",
    "United Kingdom — Free TV": "https://iptv-org.github.io/iptv/countries/uk.m3u",
    "World — Free TV": "https://iptv-org.github.io/iptv/index.m3u",
    "Germany — Free TV": "https://iptv-org.github.io/iptv/countries/de.m3u",
    "News": "https://iptv-org.github.io/iptv/categories/news.m3u",
    "Sports": "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "Music": "https://iptv-org.github.io/iptv/categories/music.m3u",
    "Movies": "https://iptv-org.github.io/iptv/categories/movies.m3u",
}

_ATTRIBUTES = re.compile(r'([\w-]+)\s*=\s*"([^"]*)"')


@dataclass(frozen=True)
class Channel:
    name: str
    url: str
    group: str = "Other"
    logo: str = ""
    tvg_id: str = ""


def _split_inf(line):
    """Split at the first comma outside a quoted EXTINF attribute."""
    quoted = False
    for index, character in enumerate(line):
        if character == '"':
            quoted = not quoted
        elif character == "," and not quoted:
            return line[:index], line[index + 1 :]
    return line, ""


def _safe_stream_url(value):
    value = value.strip().strip('"')
    if not value or any(char.isspace() for char in value):
        return ""
    parts = urlsplit(value)
    if parts.scheme.lower() not in STREAM_SCHEMES or not parts.netloc:
        return ""
    return value


def parse_m3u(content, *, deduplicate=True):
    """Parse common extended M3U; remove duplicate URL entries by default.

    An HTTP response is not proof that a stream can be played.
    """
    channels = []
    known_urls = set()
    pending = None
    for raw in content.lstrip("\ufeff").splitlines():
        line = raw.strip()
        if line.startswith("#EXTINF:"):
            details, title = _split_inf(line)
            attrs = dict(_ATTRIBUTES.findall(details))
            pending = {
                "name": title.strip() or attrs.get("tvg-name") or "Unnamed channel",
                "group": attrs.get("group-title") or "Other",
                "logo": attrs.get("tvg-logo") or "",
                "tvg_id": attrs.get("tvg-id") or "",
            }
            continue
        if not line or line.startswith("#"):
            continue

        # IPTV channel URLs must follow an EXTINF entry.
        if pending is None:
            continue
        url = _safe_stream_url(line)
        if url and (not deduplicate or url not in known_urls):
            channels.append(Channel(url=url, **pending))
            known_urls.add(url)
        pending = None
        if len(channels) >= MAX_CHANNELS:
            break
    return channels


def read_playlist(source, *, timeout=15):
    """Read a playlist from an HTTP(S) URL or local file with a size cap."""
    source = str(source).strip().strip('"')
    if not source:
        raise ValueError("Choose a playlist or enter a source URL.")
    scheme = urlsplit(source).scheme.lower()
    if scheme in ("http", "https"):
        if not urlsplit(source).netloc:
            raise ValueError("The playlist address is invalid.")
        req = Request(source, headers={"User-Agent": "BANG-IPTV-Pro/3.0"})
        with urlopen(req, timeout=timeout) as response:
            raw = response.read(MAX_PLAYLIST_BYTES + 1)
    elif "://" in source:
        raise ValueError("Playlist sources must be HTTP(S) URLs or local files.")
    else:
        file = Path(source).expanduser()
        if not file.is_file():
            raise ValueError("Playlist file not found.")
        if file.stat().st_size > MAX_PLAYLIST_BYTES:
            raise ValueError("Playlist is too large.")
        raw = file.read_bytes()
    if len(raw) > MAX_PLAYLIST_BYTES:
        raise ValueError("Playlist is too large.")
    return raw.decode("utf-8-sig", errors="replace")


def load_channels(source, *, timeout=15):
    channels = parse_m3u(read_playlist(source, timeout=timeout))
    if not channels:
        raise ValueError("No valid channels found in this playlist.")
    return channels


def filtered_channels(channels, *, query="", group="All", favorites=None):
    phrase = query.strip().casefold()
    favs = favorites if favorites is not None else None
    return [
        channel for channel in channels
        if (group == "All" or channel.group == group)
        and (not phrase or phrase in channel.name.casefold())
        and (favs is None or channel.url in favs)
    ]
