"""Build a fresh, deduplicated M3U without modifying source playlists.

Usage:
  python scripts/clean_playlists.py play.m3u deu.m3u --output cleaned.m3u
  python scripts/clean_playlists.py play.m3u --verify --output reachable.m3u
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from m3u_export import save_m3u  # noqa: E402


def parse_entries(content):
    """Read EXTINF entries, retaining their original metadata where possible."""
    import re

    items = []
    metadata = None
    for raw in content.lstrip("\ufeff").splitlines():
        line = raw.strip()
        if line.startswith("#EXTINF:"):
            if "," not in line:
                metadata = None
                continue
            attributes, name = line.split(",", 1)
            attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', attributes))
            metadata = {
                "name": name.strip() or attrs.get("tvg-name", "Untitled"),
                "category": attrs.get("group-title"),
                "logo": attrs.get("tvg-logo"),
                "tvg": {
                    "id": attrs.get("tvg-id"),
                    "name": attrs.get("tvg-name"),
                },
            }
        elif line and not line.startswith("#") and metadata is not None:
            if line.startswith(("http://", "https://")) and not any(c.isspace() for c in line):
                items.append({**metadata, "url": line})
            metadata = None
    return items


def deduplicate(channels):
    seen = set()
    unique = []
    for item in channels:
        url = item["url"]
        if url not in seen:
            seen.add(url)
            unique.append(item)
    return unique


def probe_stream(url, timeout=8):
    """Report HTTP reachability, not whether media can be decoded."""
    def attempt():
        req = Request(url, headers={
            "User-Agent": "BANG-IPTV-Playlist-Cleaner/1.0",
            "Range": "bytes=0-1023",
        })
        try:
            with urlopen(req, timeout=timeout) as response:
                return "reachable" if response.status in (200, 206) else "unknown"
        except HTTPError as error:
            if error.code in (404, 410):
                return "missing"
            return "unknown"
        except (URLError, TimeoutError, OSError, ValueError):
            return "unknown"

    first = attempt()
    if first == "missing":
        # A second explicit missing response prevents one transient 404
        # from being treated as conclusive.
        return "missing" if attempt() == "missing" else "unknown"
    return first


def clean_sources(paths, *, verify=False, workers=8):
    collected = []
    for path in paths:
        collected.extend(parse_entries(Path(path).read_text(encoding="utf-8-sig", errors="replace")))
    unique = deduplicate(collected)
    counts = {"input": len(collected), "duplicates": len(collected) - len(unique)}
    if not verify:
        return unique, {**counts, "unchecked": len(unique), "reachable": 0, "missing": 0, "unknown": 0}

    with ThreadPoolExecutor(max_workers=max(1, min(workers, 16))) as pool:
        results = list(pool.map(probe_stream, (item["url"] for item in unique)))
    report = {status: results.count(status) for status in ("reachable", "missing", "unknown")}
    # Only positively reachable URLs are exported in verification mode.
    output = [item for item, status in zip(unique, results) if status == "reachable"]
    return output, {**counts, "unchecked": 0, **report}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("playlists", nargs="+", type=Path, help="Local M3U source files")
    cli.add_argument("--output", type=Path, default=Path("cleaned.m3u"))
    cli.add_argument("--verify", action="store_true", help="Only export HTTP-reachable streams")
    cli.add_argument("--workers", type=int, default=8, help="Concurrent HTTP probes (1-16)")
    args = cli.parse_args()
    if args.output in args.playlists:
        cli.error("The output path must be different from the input files.")
    try:
        channels, report = clean_sources(args.playlists, verify=args.verify, workers=args.workers)
        save_m3u(args.output, channels)
        report["exported"] = len(channels)
        report["output"] = str(args.output)
        print(json.dumps(report, indent=2))
    except (OSError, UnicodeError, ValueError) as exc:
        cli.error(str(exc))


if __name__ == "__main__":
    main()
