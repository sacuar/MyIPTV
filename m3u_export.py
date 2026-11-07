"""Helpers for exporting playlists in the standard extended M3U format."""


def serialize_m3u(streams):
    """Return a UTF-8-ready extended M3U playlist from channel mappings.

    Ignore entries without a usable single-line URL so malformed channel data
    cannot create accidental additional M3U directives.
    """
    lines = ["#EXTM3U"]

    for stream in streams:
        url = str(stream.get("url") or "").strip()
        if not url or "\r" in url or "\n" in url:
            continue

        name = str(stream.get("name") or "Untitled channel")
        name = name.replace("\r", " ").replace("\n", " ").strip()
        lines.extend((f"#EXTINF:-1,{name}", url))

    return "\n".join(lines) + "\n"
