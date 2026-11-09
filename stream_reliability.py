"""Measured stream reliability and conservative channel replacement selection.

A successful HTTP probe only establishes reachability; a VLC playback event
is stronger evidence. None means inconclusive. Link health is local data.
"""
from __future__ import annotations

import re
import time
from urllib.parse import urlsplit


_QUALITY = re.compile(r"\s*(?:\((?:[0-9]{3,4}p|HD|FHD|SD|4K|UHD)\)|"
                      r"\[(?:[0-9]{3,4}p|HD|FHD|SD|4K|UHD)\])\s*$", re.I)
_SPACE = re.compile(r"\s+")


def canonical_name(name):
    value = str(name or "").strip()
    prev = None
    while value != prev:
        prev = value
        value = _QUALITY.sub("", value).strip()
    return _SPACE.sub(" ", value).casefold()


def same_channel(left, right):
    """Require equal TVG IDs, or exactly equal names after quality stripping."""
    a = str(left.get("tvg_id") or "").strip().casefold()
    b = str(right.get("tvg_id") or "").strip().casefold()
    if a and b:
        return a == b
    x = canonical_name(left.get("name"))
    y = canonical_name(right.get("name"))
    return bool(x and x == y)


def advertised_quality(channel):
    """Resolution is only a source-provided hint, never a measured stream quality."""
    quality = channel.get("quality") or 0
    if isinstance(quality, (int, float)) and 0 < quality <= 4320:
        return int(quality)
    label = str(channel.get("name") or "").upper()
    match = re.search(r"(?<!\d)(2160|1440|1080|720|576|480|360)P?(?!\d)", label)
    if match:
        return int(match.group(1))
    if "4K" in label or "UHD" in label:
        return 2160
    if "FHD" in label:
        return 1080
    if re.search(r"\bHD\b", label):
        return 720
    return 0


class HealthBook:
    """Track positive checks, playback success and repeated failures locally."""

    def __init__(self, entries=None):
        self.entries = {}
        if isinstance(entries, dict):
            for url, entry in entries.items():
                if isinstance(url, str) and isinstance(entry, dict) and len(url) < 4096:
                    self.entries[url] = {
                        "ok": max(0, min(int(entry.get("ok") or 0), 10000)),
                        "played": max(0, min(int(entry.get("played") or 0), 10000)),
                        "misses": max(0, min(int(entry.get("misses") or 0), 100)),
                        "status": entry.get("status") if entry.get("status") in (True, False, None) else None,
                        "checked": float(entry.get("checked") or 0),
                    }

    def status(self, url, *, now=None, max_age=1800):
        row = self.entries.get(url)
        if not row:
            return None
        current = time.time() if now is None else now
        return row["status"] if 0 <= current - row["checked"] <= max_age else None

    def record(self, url, result, *, playback=False, now=None):
        """Only repeated definite failure marks a channel dead.

        result is True / False / None. A playback success overrides HTTP
        uncertainty; a timeout never counts as a definitive failure.
        """
        current = time.time() if now is None else now
        row = self.entries.setdefault(url, {
            "ok": 0, "played": 0, "misses": 0, "status": None, "checked": 0,
        })
        if result is True:
            row["ok"] = min(10000, row["ok"] + 1)
            if playback:
                row["played"] = min(10000, row["played"] + 1)
            row["misses"] = 0
            row["status"] = True
        elif result is False:
            if current - row["checked"] > 3600:
                row["misses"] = 0
            row["misses"] = min(100, row["misses"] + 1)
            row["status"] = False if row["misses"] >= 2 else None
        else:
            # A timeout/HTTP 403 must not overturn prior confirmed evidence
            # or reset its timestamp; the cache will expire naturally.
            return row["status"]
        row["checked"] = current
        return row["status"]

    def score(self, channel, *, preference="Balanced"):
        url = channel.get("url") or ""
        row = self.entries.get(url, {})
        quality = advertised_quality(channel)
        score = min(row.get("played", 0), 8) * 15
        score += min(row.get("ok", 0), 10) * 3
        score -= min(row.get("misses", 0), 8) * 8
        if row.get("status") is False:
            score -= 100
        if url.startswith("https://"):
            score += 4
        if preference == "High quality":
            score += min(quality, 2160) / 45
        elif preference == "Data saver":
            score += 8 if 0 < quality <= 720 else (-12 if quality > 1080 else 0)
        else:
            score += 12 if 720 <= quality <= 1080 else (4 if quality > 1080 else 0)
        return score

    def snapshot(self, limit=5000):
        """Avoid growing a disk cache indefinitely."""
        rows = sorted(self.entries.items(), key=lambda entry: entry[1]["checked"], reverse=True)
        return dict(rows[:limit])


def ordered_alternatives(channel, candidates, health, *, preference="Balanced", limit=12):
    used = {channel.get("url")}
    out = []
    trusted_alts = set(channel.get("alts") or [])
    for entry in candidates:
        url = entry.get("url")
        if not url or url in used:
            continue
        if not same_channel(channel, entry) and url not in trusted_alts:
            continue
        try:
            scheme = urlsplit(url).scheme.lower()
        except ValueError:
            continue
        if scheme not in ("http", "https", "rtsp", "rtmp"):
            continue
        used.add(url)
        out.append(entry)
    out.sort(key=lambda c: health.score(c, preference=preference), reverse=True)
    return out[:max(0, limit)]


def confirm_probe(checker, url, opts=()):
    """Two explicit negative responses are needed to confirm a missing URL."""
    first = checker(url, opts)
    if first is False:
        return False if checker(url, opts) is False else None
    return first
