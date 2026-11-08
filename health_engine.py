"""Conservative background stream-health checks for BANG IPTV Pro.

HTTP reachability is not proof of playable media. Only repeated explicit
404/410 responses mark a URL offline; temporary failures stay visible.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import time


CHECK_INTERVAL_SECONDS = 300
SUSPECT_RETRY_SECONDS = 15
BATCH_SIZE = 48
MAX_WORKERS = 8


@dataclass(frozen=True)
class CheckResult:
    status: str
    reason: str = ""


@dataclass
class HealthEntry:
    status: str = "unchecked"
    missing_count: int = 0
    checked_at: float = 0.0
    reason: str = ""


def check_stream(url, *, timeout=6):
    """Probe a small portion of an HTTP stream without downloading video.

    Returns online, missing, blocked, unknown or unsupported.
    For HLS, require an actual EXT-X media/master playlist rather than 200 HTML.
    """
    try:
        parts = urlsplit(url)
        if parts.scheme.lower() not in ("http", "https") or not parts.netloc:
            return CheckResult("unsupported", "Use VLC playback to check non-HTTP streams.")
        request = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; BANG-IPTV-Pro/3.0)",
            "Accept": "*/*",
            "Range": "bytes=0-4095",
        })
        with urlopen(request, timeout=timeout) as response:
            status_code = getattr(response, "status", None) or response.getcode()
            if status_code in (404, 410):
                return CheckResult("missing", "Stream returned HTTP 404/410.")
            if status_code in (401, 403, 451):
                return CheckResult("blocked", f"Access limited (HTTP {status_code}).")
            if status_code not in (200, 206):
                return CheckResult("unknown", f"HTTP {status_code}.")

            headers = getattr(response, "headers", {})
            content_type = str(headers.get("Content-Type", "")).lower()
            path = parts.path.lower()
            is_hls = path.endswith(".m3u8") or "mpegurl" in content_type
            sample = response.read(4096)
            if not sample:
                return CheckResult("unknown", "No stream data was returned.")
            stripped = sample.lstrip(b"\xef\xbb\xbf \r\n\t")
            if is_hls:
                if stripped.startswith(b"#EXTM3U") and b"#EXT-X-" in sample:
                    return CheckResult("online", "HLS manifest responds correctly.")
                return CheckResult("unknown", "Response does not resemble a playable HLS manifest.")
            if "text/html" in content_type or stripped.startswith((b"<!DOCTYPE", b"<html", b"<HTML")):
                return CheckResult("unknown", "The URL returned a webpage, not media.")
            return CheckResult("online", "Stream endpoint returned data.")
    except HTTPError as error:
        if error.code in (404, 410):
            return CheckResult("missing", f"Stream returned HTTP {error.code}.")
        if error.code in (401, 403, 451):
            return CheckResult("blocked", f"Access limited (HTTP {error.code}).")
        return CheckResult("unknown", f"HTTP {error.code}.")
    except (URLError, TimeoutError, OSError, ValueError) as error:
        return CheckResult("unknown", f"Network or URL error: {type(error).__name__}.")


class HealthMonitor:
    """Keep channels until evidence supports hiding them; never permanently delete."""

    def __init__(self):
        self.entries = {}

    def status(self, url):
        return self.entries.get(url, HealthEntry()).status

    def record(self, url, result, *, now=None):
        if now is None:
            now = time.monotonic()
        if not isinstance(result, CheckResult):
            result = CheckResult(str(result))
        entry = self.entries.setdefault(url, HealthEntry())
        status = result.status
        if status == "missing":
            entry.missing_count += 1
            entry.status = "offline" if entry.missing_count >= 2 else "suspect"
        elif status == "playback_failed":
            entry.status = "failed"
            entry.missing_count = 0
        elif status == "playback_ok":
            entry.status = "online"
            entry.missing_count = 0
        elif entry.status == "failed" and status == "online":
            # HTTP 200 is not enough to rehabilitate a VLC playback failure.
            entry.reason = "Endpoint responds but VLC previously failed playback."
            entry.checked_at = now
            return entry.status
        else:
            entry.status = status if status in ("online", "blocked", "unknown", "unsupported") else "unknown"
            entry.missing_count = 0
        entry.checked_at = now
        entry.reason = result.reason
        return entry.status

    def choose(self, channels, *, limit=BATCH_SIZE, now=None, preferred=(), force=False):
        """Prioritise displayed channels without repeatedly checking recent results."""
        if now is None:
            now = time.monotonic()
        urls = {channel.url for channel in channels}
        order = list(dict.fromkeys(list(preferred) + [channel.url for channel in channels]))
        chosen = []
        for url in order:
            if url not in urls:
                continue
            try:
                if urlsplit(url).scheme.lower() not in ("http", "https"):
                    continue
            except ValueError:
                continue
            entry = self.entries.get(url)
            if not force and entry:
                age = now - entry.checked_at
                delay = SUSPECT_RETRY_SECONDS if entry.status == "suspect" else CHECK_INTERVAL_SECONDS
                if age < delay:
                    continue
            chosen.append(url)
            if len(chosen) >= limit:
                break
        return chosen

    def counts(self, channels):
        summary = {"online": 0, "offline": 0, "failed": 0, "blocked": 0,
                   "unknown": 0, "suspect": 0, "unchecked": 0, "unsupported": 0}
        for channel in channels:
            status = self.status(channel.url)
            summary[status if status in summary else "unknown"] += 1
        return summary


def hidden_status(status):
    """Only hide confirmed missing or player-failed channels by default."""
    return status in ("offline", "failed")
