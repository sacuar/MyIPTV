"""Conservative replacement selection for unavailable public IPTV channels.

Only exact TVG IDs or exact normalised channel names qualify. The player
checks an alternative before using it; no web search or third-party upload
of user-supplied private playlists is performed by this module.
"""

from dataclasses import replace
import re

# Remove cosmetic resolution / uptime markers, not broadcaster identity.
_QUALITY = re.compile(r"\s*(?:\((?:\d{3,4}p|HD|FHD|SD|4K|UHD)\)|"
                      r"\[(?:not 24/7|geo-blocked|geo blocked)\])\s*$", re.I)
_SPACE = re.compile(r"\s+")


def normalized_name(value):
    name = str(value or "").strip()
    previous = None
    while name != previous:
        previous = name
        name = _QUALITY.sub("", name).strip()
    return _SPACE.sub(" ", name).casefold()


def matching_alternatives(channel, available, *, limit=12):
    """Find plausible alternatives from a trusted, already-loaded playlist.

    Prefer identical nonblank TVG IDs. Otherwise require exact names.
    Never return the same URL twice, or the URL that just failed.
    """
    target_id = str(channel.tvg_id or "").strip().casefold()
    target_name = normalized_name(channel.name)
    matches = []
    used = {channel.url}
    for candidate in available:
        if candidate.url in used:
            continue
        candidate_id = str(candidate.tvg_id or "").strip().casefold()
        same_id = bool(target_id and candidate_id and target_id == candidate_id)
        same_name = bool(target_name and target_name == normalized_name(candidate.name))
        if not same_id and not same_name:
            continue
        used.add(candidate.url)
        priority = 0 if same_id else 1
        # HTTPS and matching language/group are good tie-breakers, not identity.
        https = candidate.url.startswith("https://")
        matches.append((priority, 0 if https else 1, candidate))
    matches.sort(key=lambda item: (item[0], item[1]))
    return [entry[2] for entry in matches[:max(0, limit)]]


def first_reachable_replacement(channel, available, check, *, limit=8):
    """Return the first candidate whose manifest/endpoint probe is positive.

    A network probe is not proof that VLC can decode the stream.
    """
    for candidate in matching_alternatives(channel, available, limit=limit):
        try:
            if check(candidate.url).status == "online":
                return candidate
        except (OSError, ValueError, TimeoutError):
            continue
    return None


def apply_replacements(channels, replacements):
    """Reapply locally known fixes whenever the source M3U refreshes.

    Skip repeated URLs and follow at most four replacement hops.
    """
    result = []
    seen = set()
    for channel in channels:
        current_url = channel.url
        visited = {current_url}
        for _ in range(4):
            next_url = replacements.get(current_url)
            if not next_url or next_url in visited:
                break
            current_url = next_url
            visited.add(next_url)
        if current_url not in seen:
            result.append(replace(channel, url=current_url))
            seen.add(current_url)
    return result
