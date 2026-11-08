#!/usr/bin/env python3
"""
BANG IPTV Pro v4.0
==================
What's new compared to v3:
  * Channel logos      - cached on disk, loaded lazily for the rows you can see, big logo in the player
  * Live update        - playlist auto-refreshes (conditional download), keeps link status, shows +new / -removed
  * Broken link repair - dead links are detected while playing and replaced automatically with a working
                         alternative (same tvg-id / same channel name from any loaded playlist); fixes are
                         remembered. Right click -> "Fix broken link", or "Fix all dead links".
  * More live media    - 30 countries, 30 categories, 12 languages, merged "mega packs", custom URL, local M3U
  * Full screen        - video only, auto-hiding control bar, channel name overlay, double-click, Esc
  * Better sorting     - 8 sort modes, clickable column headers, pin favourites, status/category/search filters,
                         natural number ordering (Channel 2 before Channel 10), quality (1080p/720p...) ordering
  * Much faster link checking (parallel) and a real stream check (not just HTTP status)
"""

import os
import sys
import re
import io
import json
import time
import queue
import hashlib
import difflib
import threading
import subprocess
import urllib.parse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

APP_NAME = "BANG IPTV"
APP_VERSION = "4.0 Beta 1"


def _ensure(module, pip_name=None):
    """Load optional dependencies; never install packages at application startup."""
    try:
        return __import__(module)
    except (ImportError, OSError):
        return None


try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog, filedialog
except ImportError:  # lets the logic below be imported/tested on machines without Tk
    tk = ttk = messagebox = simpledialog = filedialog = None

requests = _ensure("requests")
BeautifulSoup = None
_bs4 = _ensure("bs4", "beautifulsoup4")
if _bs4:
    BeautifulSoup = _bs4.BeautifulSoup
_VLC_DLL_HANDLE = None

def _prepare_vlc():
    global _VLC_DLL_HANDLE
    if sys.platform != "win32":
        return
    for root in (os.environ.get("PROGRAMFILES", r"C:\\Program Files"),
                 os.environ.get("PROGRAMFILES(X86)", r"C:\\Program Files (x86)")):
        folder = Path(root) / "VideoLAN" / "VLC"
        lib = folder / "libvlc.dll"
        if lib.exists():
            os.environ.setdefault("PYTHON_VLC_LIB_PATH", str(lib))
            os.environ.setdefault("PYTHON_VLC_MODULE_PATH", str(folder / "plugins"))
            if hasattr(os, "add_dll_directory"):
                _VLC_DLL_HANDLE = os.add_dll_directory(str(folder))
            break

_prepare_vlc()
vlc = _ensure("vlc", "python-vlc")
PIL_OK = False
ImageTk = None
if _ensure("PIL", "pillow"):
    try:
        from PIL import Image, ImageDraw, ImageFont
        PIL_OK = True
        try:
            from PIL import ImageTk      # needs tkinter
        except Exception:
            ImageTk = None
            PIL_OK = False
    except Exception:
        PIL_OK = False

# ============================================
# CONFIGURATION
# ============================================

# UI-only link visibility gate, not encryption or protection from source inspection.
PASSWORD_HASH = "8d23cf6c86e834a7aa6eded54c26ce2bb2e74903538c61bdd5d2197997ab2f72"

def _default_data_dir():
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local")) / "BANGIPTV"
    return Path.home() / ".config" / "bang-iptv"


# Keep settings, favourites and repair records outside PyInstaller's temporary folder.
APP_DIR = Path(os.environ.get("BANG_IPTV_DIR") or _default_data_dir())
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
MAX_CHANNELS = 30000

DEFAULT_SETTINGS = {
    "volume": 70,
    "last_source": "🇧🇩 Bangladesh (iptv-org)",
    "sort": "Name (A→Z)",
    "pin_favs": True,
    "status_filter": "Hide dead",
    "live_update": True,
    "refresh_minutes": 30,
    "auto_fix": True,
    "custom_sources": [],
}

# ============================================
# IPTV SOURCES
# ============================================

IPTV_SOURCES = {
    "🌍 World IPTV": {"urls": ["https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8"],
                      "desc": "5,000+ channels worldwide"},
    "📺 Global TV": {"urls": ["https://iptv-org.github.io/iptv/index.m3u"], "desc": "10,000+ channels"},
    "🇧🇩 Bangladesh IPTV": {"urls": ["https://raw.githubusercontent.com/sacuar/MyIPTV/main/play.m3u"],
                            "desc": "Bangladeshi channels - BTV, Channel i, NTV, Somoy TV"},
    "🇧🇩 BDIX IPTV": {"urls": ["https://raw.githubusercontent.com/time2shine/IPTV/refs/heads/master/combined.m3u"],
                      "desc": "BDIX supported, 600+ channels"},
    "🇧🇩 Bangladesh (iptv-org)": {"urls": ["https://iptv-org.github.io/iptv/countries/bd.m3u"],
                                  "desc": "iptv-org Bangladesh channels"},
    "🇬🇧 UK Free": {"urls": ["https://iptv-org.github.io/iptv/countries/gb.m3u"], "desc": "UK channels"},
    "🇺🇸 US Free": {"urls": ["https://iptv-org.github.io/iptv/countries/us.m3u"], "desc": "US channels"},
    "📰 News": {"urls": ["https://iptv-org.github.io/iptv/categories/news.m3u"], "desc": "News channels worldwide"},
    "⚽ Sports": {"urls": ["https://iptv-org.github.io/iptv/categories/sports.m3u"], "desc": "Sports channels"},
    "🎵 Music": {"urls": ["https://iptv-org.github.io/iptv/categories/music.m3u"], "desc": "Music channels"},
    "🎬 Movies": {"urls": ["https://iptv-org.github.io/iptv/categories/movies.m3u"], "desc": "Movie channels"},
}


def _flag(cc):
    return "".join(chr(0x1F1E6 + ord(c) - 65) for c in cc.upper())


COUNTRIES = {
    "in": "India", "pk": "Pakistan", "lk": "Sri Lanka", "np": "Nepal", "ca": "Canada", "au": "Australia",
    "ae": "UAE", "sa": "Saudi Arabia", "qa": "Qatar", "tr": "Turkey", "fr": "France", "de": "Germany",
    "es": "Spain", "it": "Italy", "ru": "Russia", "br": "Brazil", "jp": "Japan", "kr": "South Korea",
    "cn": "China", "id": "Indonesia", "my": "Malaysia", "sg": "Singapore", "eg": "Egypt", "za": "South Africa",
    "ng": "Nigeria", "mx": "Mexico", "ar": "Argentina", "nl": "Netherlands", "pl": "Poland", "th": "Thailand",
}
CATEGORIES = ["animation", "auto", "business", "classic", "comedy", "cooking", "culture", "documentary",
              "education", "entertainment", "family", "general", "interactive", "kids", "legislative",
              "lifestyle", "outdoor", "public", "relax", "religious", "science", "series", "shop", "travel",
              "weather"]
LANGUAGES = {"ben": "Bengali", "hin": "Hindi", "urd": "Urdu", "eng": "English", "ara": "Arabic", "tam": "Tamil",
             "tel": "Telugu", "spa": "Spanish", "fra": "French", "zho": "Chinese", "tur": "Turkish",
             "rus": "Russian"}

_B = "https://iptv-org.github.io/iptv"
for _cc, _nm in COUNTRIES.items():
    IPTV_SOURCES[f"{_flag(_cc)} {_nm}"] = {"urls": [f"{_B}/countries/{_cc}.m3u"], "desc": f"{_nm} channels"}
for _c in CATEGORIES:
    IPTV_SOURCES[f"📂 {_c.title()}"] = {"urls": [f"{_B}/categories/{_c}.m3u"], "desc": f"{_c} channels"}
for _l, _nm in LANGUAGES.items():
    IPTV_SOURCES[f"🗣 {_nm}"] = {"urls": [f"{_B}/languages/{_l}.m3u"], "desc": f"{_nm} language channels"}

IPTV_SOURCES["🇧🇩 Bangladesh MEGA (all BD lists)"] = {
    "urls": [f"{_B}/countries/bd.m3u", f"{_B}/languages/ben.m3u",
             "https://raw.githubusercontent.com/sacuar/MyIPTV/main/play.m3u",
             "https://raw.githubusercontent.com/time2shine/IPTV/refs/heads/master/combined.m3u"],
    "desc": "Every Bangladeshi / Bengali list merged and de-duplicated"}
IPTV_SOURCES["🌏 South Asia pack (BD+IN+PK+LK+NP)"] = {
    "urls": [f"{_B}/countries/{c}.m3u" for c in ("bd", "in", "pk", "lk", "np")],
    "desc": "Bangladesh, India, Pakistan, Sri Lanka, Nepal"}
IPTV_SOURCES["🌐 MEGA pack (all major sources)"] = {
    "urls": [f"{_B}/index.m3u", "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8",
             "https://raw.githubusercontent.com/sacuar/MyIPTV/main/play.m3u",
             "https://raw.githubusercontent.com/time2shine/IPTV/refs/heads/master/combined.m3u"],
    "desc": "Everything merged - biggest list, takes longer"}

# ============================================
# VIDEO SEARCH SOURCES (unchanged from v3)
# ============================================

VIDEO_SOURCES = {
    "FluxTV": {"url": "https://fluxtv.cc", "search": "/search?q={query}", "type": "Movies & TV"},
    "KissKH": {"url": "https://kisskh.do", "search": "/search?q={query}", "type": "Asian Dramas"},
    "FullxCinema": {"url": "https://fullxcinema.com", "search": "/?s={query}", "type": "Movies"},
    "Cat3Movie": {"url": "https://www.cat3movie.club", "search": "/?s={query}", "type": "Asian Movies"},
}

SORT_MODES = ["Playlist order", "Name (A→Z)", "Name (Z→A)", "Category → Name", "Working first",
              "Favorites first", "Recently watched", "Quality (high→low)"]
STATUS_FILTERS = ["All", "Working only", "Unchecked", "Dead only", "Hide dead"]


# ============================================
# PURE LOGIC (no GUI) - parsing, sorting, matching
# ============================================

def jload(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def jsave(path, data):
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception as e:
        print("save failed:", path, e)


ATTR_RE = re.compile(r'([\w\-]+)="([^"]*)"')
QUALITY_RE = re.compile(r'(2160|1440|1080|720|576|540|480|360|240)\s*[pP]')


def quality_of(name):
    m = QUALITY_RE.search(name or "")
    if m:
        return int(m.group(1))
    low = (name or "").lower()
    if "4k" in low or "uhd" in low:
        return 2160
    if "fhd" in low:
        return 1080
    if re.search(r'\bhd\b', low):
        return 720
    return 0


def norm_name(name):
    s = (name or "").lower()
    s = re.sub(r'[\(\[\{].*?[\)\]\}]', ' ', s)
    s = re.sub(r'\b(hd|fhd|uhd|sd|4k|hevc|h264|h\.264|hq|lq|backup|alt)\b', ' ', s)
    return re.sub(r'[\W_]+', '', s)


def natural_key(s):
    s = re.sub(r'^[^\w]+', '', (s or "").casefold())
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', s)]


def _kodi_headers(url):
    """url|User-Agent=x&Referer=y  ->  (clean url, [vlc options])"""
    if "|" not in url:
        return url, []
    base, _, hdr = url.partition("|")
    opts = []
    for part in hdr.split("&"):
        k, _, v = part.partition("=")
        k = k.strip().lower()
        v = urllib.parse.unquote(v.strip())
        if k in ("user-agent", "useragent"):
            opts.append(":http-user-agent=" + v)
        elif k in ("referer", "referrer"):
            opts.append(":http-referrer=" + v)
    return base, opts


def parse_m3u(text, source=""):
    """Parse an M3U/M3U8 playlist into channel dicts."""
    chans, cur, opts = [], None, []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#EXTINF"):
            masked = re.sub(r'"[^"]*"', lambda m: "x" * len(m.group(0)), line)
            comma = masked.find(",")   # first comma outside quotes: names may contain commas
            name = line[comma + 1:].strip() if comma != -1 else ""
            attrs = {k.lower(): v for k, v in ATTR_RE.findall(line[:comma] if comma != -1 else line)}
            cat = (attrs.get("group-title") or "Uncategorized").split(";")[0].strip() or "Uncategorized"
            cur = {"name": name or attrs.get("tvg-name", ""), "category": cat, "logo": attrs.get("tvg-logo", ""),
                   "tvg_id": attrs.get("tvg-id", ""), "country": attrs.get("tvg-country", ""),
                   "language": attrs.get("tvg-language", "")}
            opts = []
        elif line.startswith("#EXTVLCOPT:"):
            opts.append(":" + line[len("#EXTVLCOPT:"):].strip())
        elif line.startswith("#EXTGRP:") and cur is not None:
            cur["category"] = line[8:].strip() or cur["category"]
        elif line.startswith("#"):
            continue
        else:
            if "://" not in line:
                cur, opts = None, []
                continue
            url, kodi = _kodi_headers(line)
            if cur is None:
                cur = {"name": url.rsplit("/", 1)[-1][:60], "category": "Uncategorized", "logo": "",
                       "tvg_id": "", "country": "", "language": ""}
            if not cur["name"]:
                cur["name"] = f"Channel {len(chans) + 1}"
            ch = dict(cur)
            ch.update({"url": url, "opts": opts + kodi, "working": None, "checked": 0, "alts": [],
                       "quality": quality_of(cur["name"]), "norm": norm_name(cur["name"]), "source": source})
            chans.append(ch)
            cur, opts = None, []
    return chans


def merge_playlists(lists, overrides=None, limit=MAX_CHANNELS):
    """Merge several parsed playlists, de-duplicate by URL, apply remembered link fixes,
    and record same-name alternative URLs (used later for link repair)."""
    overrides = overrides or {}
    seen, out = {}, []
    for chans in lists:
        for ch in chans:
            url = overrides.get(ch["url"], ch["url"])
            ch["url"] = url
            if url in seen:
                continue
            seen[url] = ch
            out.append(ch)
            if len(out) >= limit:
                break
        if len(out) >= limit:
            break
    by_key = {}
    for ch in out:
        key = ch["tvg_id"] or ch["norm"]
        if key:
            by_key.setdefault(key, []).append(ch)
    for group in by_key.values():
        if len(group) > 1:
            for ch in group:
                ch["alts"] = [o["url"] for o in group if o is not ch][:8]
    for i, ch in enumerate(out):
        ch["_i"] = i
    return out


def is_favorite(ch, favorites):
    for f in favorites:
        if f.get("url") and f["url"] == ch["url"]:
            return True
        if f.get("tvg_id") and f["tvg_id"] == ch.get("tvg_id"):
            return True
        if not f.get("url") and f.get("name") == ch["name"]:
            return True
    return False


def sort_channels(chans, mode, favorites=(), recent=(), pin_favs=False):
    """Return a new, sorted list. `recent` is a list of URLs, newest first."""
    rank = {u: i for i, u in enumerate(recent)}
    name_key = lambda c: natural_key(c["name"])  # noqa: E731
    status_rank = lambda c: 0 if c.get("working") is True else (1 if c.get("working") is None else 2)  # noqa: E731
    fav_set = [is_favorite(c, favorites) for c in chans] if (pin_favs or mode == "Favorites first") else None
    idx = {id(c): n for n, c in enumerate(chans)}
    isfav = lambda c: fav_set[idx[id(c)]] if fav_set is not None else False  # noqa: E731
    keys = {
        "Playlist order": lambda c: c.get("_i", 0),
        "Name (A→Z)": name_key,
        "Category → Name": lambda c: (natural_key(c.get("category", "")), name_key(c)),
        "Working first": lambda c: (status_rank(c), name_key(c)),
        "Favorites first": lambda c: (0 if isfav(c) else 1, name_key(c)),
        "Recently watched": lambda c: (rank.get(c["url"], 10 ** 6), name_key(c)),
        "Quality (high→low)": lambda c: (-c.get("quality", 0), name_key(c)),
    }
    if mode == "Name (Z→A)":
        out = sorted(chans, key=name_key, reverse=True)
    else:
        out = sorted(chans, key=keys.get(mode, name_key))
    if pin_favs and mode != "Favorites first":
        out = [c for c in out if isfav(c)] + [c for c in out if not isfav(c)]
    return out


def filter_channels(chans, category="All", query="", status="All"):
    q = [t for t in (query or "").lower().split() if t]
    out = []
    for c in chans:
        if category != "All" and c.get("category", "Uncategorized") != category:
            continue
        w = c.get("working")
        if status == "Working only" and w is not True:
            continue
        if status == "Unchecked" and w is not None:
            continue
        if status == "Dead only" and w is not False:
            continue
        if status == "Hide dead" and w is False:
            continue
        if q:
            hay = f"{c['name']} {c.get('category', '')} {c.get('tvg_id', '')}".lower()
            if not all(t in hay for t in q):
                continue
        out.append(c)
    return out


def check_stream(url, opts=(), timeout=6):
    """True when the URL really looks like a live stream / playlist (not just 'HTTP 200')."""
    if requests is None:
        return None  # missing network support is not evidence of a working stream
    r = None
    try:
        headers = dict(UA)
        for o in opts:
            if o.startswith(":http-user-agent="):
                headers["User-Agent"] = o.split("=", 1)[1]
            elif o.startswith(":http-referrer="):
                headers["Referer"] = o.split("=", 1)[1]
        r = requests.get(url, headers=headers, timeout=timeout, stream=True, allow_redirects=True)
        if r.status_code in (404, 410):
            return False
        if r.status_code >= 400:
            return None  # access control, geography, rate limiting are inconclusive
        ctype = r.headers.get("content-type", "").lower()
        if "text/html" in ctype:
            return None  # a portal/login page is not proof of permanent failure
        first = next(r.iter_content(4096), b"")
        if not first:
            return None
        path = url.lower().split("?")[0]
        if path.endswith((".m3u8", ".m3u")) or "mpegurl" in ctype:
            return first.lstrip(b"\xef\xbb\xbf \r\n\t").startswith(b"#EXTM3U")
        return True
    except Exception:
        return None  # preserve channels when connections time out or fail temporarily
    finally:
        if r is not None:
            try:
                r.close()
            except Exception:
                pass


class Repairer:
    """Index of every channel we have ever seen, used to find a working replacement for a dead link."""

    def __init__(self):
        self.lock = threading.Lock()
        self.by_id, self.by_norm, self.by_prefix = {}, {}, {}
        self.urls = set()

    def add(self, chans):
        with self.lock:
            for c in chans:
                if c["url"] in self.urls:
                    continue
                self.urls.add(c["url"])
                if c.get("tvg_id"):
                    self.by_id.setdefault(c["tvg_id"], []).append(c)
                n = c.get("norm")
                if n:
                    lst = self.by_norm.setdefault(n, [])
                    lst.append(c)
                    if len(lst) == 1:
                        self.by_prefix.setdefault(n[:2], []).append(n)

    def candidates(self, ch, exclude=(), limit=12):
        """Channel dicts that are plausibly the same channel, best matches first."""
        seen = set(exclude) | {ch["url"]}
        out = []

        def push(c):
            if c["url"] not in seen and len(out) < limit * 2:
                seen.add(c["url"])
                out.append(c)

        with self.lock:
            for u in ch.get("alts", []):
                push({"url": u, "opts": [], "quality": 0})
            if ch.get("tvg_id"):
                for c in self.by_id.get(ch["tvg_id"], []):
                    push(c)
            n = ch.get("norm")
            if n:
                for c in self.by_norm.get(n, []):
                    push(c)
                if len(out) < limit:
                    sm = difflib.SequenceMatcher(autojunk=False)
                    sm.set_seq2(n)
                    for other in self.by_prefix.get(n[:2], []):
                        if other == n or abs(len(other) - len(n)) > 3:
                            continue
                        if re.sub(r"\D", "", other) != re.sub(r"\D", "", n):
                            continue          # 'Channel 8' must never match 'Channel 9'
                        sm.set_seq1(other)
                        if sm.real_quick_ratio() >= 0.88 and sm.quick_ratio() >= 0.88 and sm.ratio() >= 0.88:
                            for c in self.by_norm[other]:
                                push(c)
        out.sort(key=lambda c: (not c["url"].startswith("https"), -c.get("quality", 0)))
        return out[:limit]

    def find_working(self, ch, exclude=(), checker=None, workers=8):
        checker = checker or check_stream
        cands = self.candidates(ch, exclude)
        if not cands:
            return None
        with ThreadPoolExecutor(max_workers=min(workers, len(cands))) as ex:
            futs = {ex.submit(checker, c["url"], c.get("opts", [])): c for c in cands}
            winner = None
            for f in as_completed(futs):
                try:
                    ok = f.result()
                except Exception:
                    ok = False
                if ok:
                    winner = futs[f]
                    break
            for f in futs:
                f.cancel()
        return winner


def fmt_time(ms):
    s = max(0, int(ms // 1000))
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


# ============================================
# LOGOS
# ============================================

class LogoStore:
    """Downloads channel logos in worker threads, caches them as small PNGs on disk."""

    def __init__(self, folder):
        self.dir = Path(folder) / "logos"
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, url):
        return self.dir / (hashlib.sha1(url.encode("utf-8")).hexdigest() + ".png")

    @staticmethod
    def fit(img, size):
        img = img.convert("RGBA")
        img.thumbnail((size, size))
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2), img)
        return canvas

    def load(self, url, size=32):
        """Worker thread. Returns a PIL image or None."""
        if not (PIL_OK and requests and url and url.startswith("http")):
            return None
        p = self._path(url)
        bad = p.with_suffix(".bad")
        try:
            if p.exists() and p.stat().st_size > 0:
                img = Image.open(p)
                img.load()
                return self.fit(img, size)
            if bad.exists() and time.time() - bad.stat().st_mtime < 86400:
                return None
            r = requests.get(url, headers=UA, timeout=8)
            r.raise_for_status()
            if len(r.content) > 3_000_000:
                raise ValueError("too big")
            img = Image.open(io.BytesIO(r.content))
            img.load()
            img = img.convert("RGBA")
            img.thumbnail((128, 128))
            img.save(p, "PNG")
            return self.fit(img, size)
        except Exception:
            try:
                bad.touch()
            except OSError:
                pass
            return None

    @staticmethod
    def placeholder(name, size=32):
        """Coloured tile with the channel's initials."""
        if not PIL_OK:
            return None
        h = int(hashlib.md5((name or "?").encode("utf-8")).hexdigest()[:6], 16)
        colour = (60 + h % 120, 60 + (h >> 8) % 120, 60 + (h >> 16) % 120, 255)
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, size - 1, size - 1), radius=size // 5, fill=colour)
        words = re.findall(r"\w+", name or "?")
        txt = "".join(w[0] for w in words[:2]).upper() or "?"
        try:
            font = ImageFont.truetype("arial.ttf", size // 2)
        except Exception:
            font = ImageFont.load_default()
        try:
            box = d.textbbox((0, 0), txt, font=font)
            tw, th = box[2] - box[0], box[3] - box[1]
            d.text(((size - tw) / 2 - box[0], (size - th) / 2 - box[1]), txt, fill=(255, 255, 255, 255), font=font)
        except Exception:
            d.text((size // 4, size // 4), txt, fill=(255, 255, 255, 255))
        return img


# ============================================
# MAIN IPTV PLAYER
# ============================================

class IPTVPro:
    ROW_H = 38
    LOGO = 30

    def __init__(self, root):
        self.root = root
        self.root.title(f"🎬 {APP_NAME} v{APP_VERSION}")
        self.root.geometry("1400x900")
        self.root.minsize(1100, 700)
        self.root.configure(bg="#0d0d0d")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.is_closing = False
        self.is_authenticated = False

        APP_DIR.mkdir(parents=True, exist_ok=True)
        self.migrate_legacy_files()

        try:
            self.instance = vlc.Instance("--no-xlib") if (vlc and sys.platform.startswith("linux")) else vlc.Instance()
            self.player = self.instance.media_player_new()
            self.player.video_set_mouse_input(False)
            self.player.video_set_key_input(False)
        except Exception as e:
            messagebox.showerror("VLC Error", f"Could not start VLC: {e}\n\nInstall VLC (same 32/64-bit as Python) "
                                              f"and run:  pip install python-vlc")
            self.ok = False
            self.root.destroy()
            return
        self.ok = True

        # state
        self.is_playing = self.is_paused = False
        self.channels, self.categories = [], {}
        self.view = []                 # channels currently shown, in display order
        self.by_iid = {}
        self.current = None            # channel dict being played
        self.play_started = 0.0
        self.seen_playing = False
        self.cur_is_live = False
        self.fix_attempted = False
        self.fullscreen = False
        self.seeking = False
        self.loading_gen = 0
        self.last_update = None
        self._last_filter_redraw = 0.0
        self.links_relock_job = None
        self.http_cache = {}
        self.display_gen = 0

        self.settings = dict(DEFAULT_SETTINGS)
        self.settings.update(jload(APP_DIR / "settings.json", {}))
        if self.settings.get("status_filter") not in STATUS_FILTERS:
            self.settings["status_filter"] = "Hide dead"
        self.favorites = self.normalize_saved(jload(APP_DIR / "favorites.json", []))
        self.history = self.normalize_saved(jload(APP_DIR / "history.json", []))
        self.overrides = jload(APP_DIR / "link_overrides.json", {})
        self.repairer = Repairer()
        self.logos = LogoStore(APP_DIR)

        # thread -> UI plumbing (tkinter is not thread safe: workers only post callables here)
        self.uiq = queue.Queue()
        self.logo_pool = ThreadPoolExecutor(max_workers=6)
        self.val_pool = None
        self.val_gen = 0
        self.val_buf, self.val_lock = [], threading.Lock()
        self.val_total = self.val_done = 0
        self.logo_img = {}             # (url,size) -> PhotoImage
        self.logo_req = set()
        self.placeholders = {}
        self.default_icon = None

        self.setup_style()
        self.setup_ui()
        self.setup_shortcuts()
        self.root.after(50, self.pump_ui)
        self.root.after(500, self.tick)
        self.root.after(60000, self.live_update_check)
        self.root.after(5 * 60000, self.recheck_loop)

        self.set_status("Loading saved playlist automatically...")
        self.load_source(self.settings.get("last_source") if self.settings.get("last_source") in self.all_sources()
                         else "🌍 World IPTV")

    # ---------------------------------------------------------------- plumbing
    def call_ui(self, fn, *a):
        self.uiq.put((fn, a))

    def pump_ui(self):
        try:
            for _ in range(200):
                fn, a = self.uiq.get_nowait()
                try:
                    fn(*a)
                except Exception as e:
                    print("ui error:", e)
        except queue.Empty:
            pass
        if not self.is_closing:
            self.root.after(50, self.pump_ui)

    def migrate_legacy_files(self):
        for old, new in (("favorites.json", "favorites.json"), ("history.json", "history.json"),
                         ("bang_iptv_settings.json", "settings.json")):
            if Path(old).exists() and not (APP_DIR / new).exists():
                try:
                    (APP_DIR / new).write_bytes(Path(old).read_bytes())
                except OSError:
                    pass

    @staticmethod
    def normalize_saved(items):
        """v3 stored plain names; v4 stores {name,url,logo,tvg_id}."""
        out = []
        for it in items or []:
            if isinstance(it, str):
                out.append({"name": it, "url": "", "logo": "", "tvg_id": ""})
            elif isinstance(it, dict) and it.get("name"):
                out.append({"name": it["name"], "url": it.get("url", ""), "logo": it.get("logo", ""),
                            "tvg_id": it.get("tvg_id", "")})
        return out

    def save_all(self):
        jsave(APP_DIR / "settings.json", self.settings)
        jsave(APP_DIR / "favorites.json", self.favorites)
        jsave(APP_DIR / "history.json", self.history)
        jsave(APP_DIR / "link_overrides.json", self.overrides)

    def set_status(self, text):
        self.status.config(text=text)

    def all_sources(self):
        d = dict(IPTV_SOURCES)
        for cs in self.settings.get("custom_sources", []):
            d[f"⭐ {cs['name']}"] = {"urls": [cs["url"]], "desc": "Custom"}
        return d

    # ---------------------------------------------------------------- style
    def setup_style(self):
        st = ttk.Style()
        try:
            st.theme_use("clam")
        except Exception:
            pass
        bg, fg = "#1a1a1a", "#ffffff"
        st.configure("Ch.Treeview", background=bg, fieldbackground=bg, foreground=fg, rowheight=self.ROW_H,
                     borderwidth=0, font=("Segoe UI", 10))
        st.map("Ch.Treeview", background=[("selected", "#ff3b30")], foreground=[("selected", "#ffffff")])
        st.configure("Ch.Treeview.Heading", background="#232323", foreground="#bbbbbb", relief="flat",
                     font=("Segoe UI", 9, "bold"))
        st.map("Ch.Treeview.Heading", background=[("active", "#333333")])
        st.configure("TNotebook", background="#0d0d0d", borderwidth=0)
        st.configure("TNotebook.Tab", background="#1a1a1a", foreground="#cccccc", padding=(14, 6))
        st.map("TNotebook.Tab", background=[("selected", "#ff3b30")], foreground=[("selected", "#ffffff")])
        st.configure("TFrame", background="#0d0d0d")
        st.configure("TCombobox", fieldbackground="#1a1a1a", background="#2a2a2a", foreground="#ffffff",
                     arrowcolor="#ffffff")
        st.map("TCombobox", fieldbackground=[("readonly", "#1a1a1a")], foreground=[("readonly", "#ffffff")])
        self.root.option_add("*TCombobox*Listbox.background", "#1a1a1a")
        self.root.option_add("*TCombobox*Listbox.foreground", "#ffffff")
        self.root.option_add("*TCombobox*Listbox.selectBackground", "#ff3b30")

    # ---------------------------------------------------------------- UI
    def setup_ui(self):
        # The video container lives directly under root so it can be moved to full screen
        # without re-embedding VLC. It is positioned over `video_slot` with place(in_=...).
        self.video_container = tk.Frame(self.root, bg="#000000")
        self.main_frame = tk.Frame(self.root, bg="#0d0d0d")
        self.setup_status_bar()
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.setup_top_bar(self.main_frame)
        self.setup_tabs(self.main_frame)
        self.build_video_container()
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.root.after(200, self.place_video)

    def setup_status_bar(self):
        self.status = tk.Label(self.root, text="Ready", font=("Segoe UI", 9), fg="#888888", bg="#1a1a1a",
                               anchor=tk.W, padx=10)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def btn(self, parent, text, cmd, fg="#ffffff", **kw):
        b = tk.Button(parent, text=text, command=cmd, bg="#1a1a1a", fg=fg, bd=0, activebackground="#2a2a2a",
                      activeforeground=fg, cursor="hand2", **kw)
        b.bind("<Enter>", lambda e: b.config(bg="#2a2a2a"))
        b.bind("<Leave>", lambda e: b.config(bg="#1a1a1a"))
        return b

    def setup_top_bar(self, parent):
        top = tk.Frame(parent, bg="#0d0d0d")
        top.pack(fill=tk.X, pady=(0, 8))
        tk.Label(top, text="🎬 BANG IPTV Pro", font=("Segoe UI", 18, "bold"), fg="#ff3b30", bg="#0d0d0d").pack(
            side=tk.LEFT, padx=5)

        tk.Label(top, text="Source:", font=("Segoe UI", 10), fg="#888888", bg="#0d0d0d").pack(side=tk.LEFT, padx=(15, 3))
        self.source_var = tk.StringVar(value=self.settings.get("last_source"))
        self.source_menu = ttk.Combobox(top, textvariable=self.source_var, values=list(self.all_sources().keys()),
                                        width=34, state="readonly")
        self.source_menu.pack(side=tk.LEFT, padx=3)
        self.source_menu.bind("<<ComboboxSelected>>", lambda e: self.load_selected_source())

        self.btn(top, "📥 Load", self.load_selected_source, padx=10, pady=4).pack(side=tk.LEFT, padx=2)
        self.btn(top, "🔄 Update now", lambda: self.load_source(self.source_var.get(), silent=True), padx=10,
                 pady=4).pack(side=tk.LEFT, padx=2)
        self.btn(top, "➕ URL", self.add_custom_source, padx=8, pady=4).pack(side=tk.LEFT, padx=2)
        self.btn(top, "📂 File", self.open_m3u_file, padx=8, pady=4).pack(side=tk.LEFT, padx=2)
        self.btn(top, "🔧 Fix dead links", self.fix_all_dead, padx=8, pady=4).pack(side=tk.LEFT, padx=2)
        self.link_btn = self.btn(top, "🔒 Links Hidden", self.toggle_link_visibility, fg="#ff3b30", padx=10, pady=4)
        self.link_btn.pack(side=tk.LEFT, padx=2)

        right = tk.Frame(top, bg="#0d0d0d")
        right.pack(side=tk.RIGHT)
        self.live_var = tk.BooleanVar(value=self.settings.get("live_update", True))
        tk.Checkbutton(right, text="Live update every", variable=self.live_var, command=self.on_live_toggle,
                       bg="#0d0d0d", fg="#bbbbbb", selectcolor="#1a1a1a", activebackground="#0d0d0d",
                       activeforeground="#ffffff").pack(side=tk.LEFT)
        self.refresh_var = tk.StringVar(value=str(self.settings.get("refresh_minutes", 30)))
        cb = ttk.Combobox(right, textvariable=self.refresh_var, values=["5", "10", "15", "30", "60", "120"], width=4,
                          state="readonly")
        cb.pack(side=tk.LEFT)
        cb.bind("<<ComboboxSelected>>", self.on_live_toggle)
        tk.Label(right, text="min", fg="#bbbbbb", bg="#0d0d0d").pack(side=tk.LEFT, padx=(2, 8))
        self.fix_var = tk.BooleanVar(value=self.settings.get("auto_fix", True))
        tk.Checkbutton(right, text="Auto-fix links", variable=self.fix_var, command=self.on_live_toggle,
                       bg="#0d0d0d", fg="#bbbbbb", selectcolor="#1a1a1a", activebackground="#0d0d0d",
                       activeforeground="#ffffff").pack(side=tk.LEFT)

        info = tk.Frame(parent, bg="#0d0d0d")
        info.pack(fill=tk.X, pady=(0, 4))
        self.source_status = tk.Label(info, text="", font=("Segoe UI", 9), fg="#888888", bg="#0d0d0d")
        self.source_status.pack(side=tk.LEFT, padx=5)
        self.update_label = tk.Label(info, text="", font=("Segoe UI", 9), fg="#888888", bg="#0d0d0d")
        self.update_label.pack(side=tk.LEFT, padx=10)
        self.link_count_label = tk.Label(info, text="", font=("Segoe UI", 9), fg="#888888", bg="#0d0d0d")
        self.link_count_label.pack(side=tk.RIGHT, padx=5)

    def setup_tabs(self, parent):
        self.tab_control = ttk.Notebook(parent)
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        self.iptv_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.iptv_tab, text="📺 IPTV Channels")
        self.setup_iptv_tab(self.iptv_tab)
        self.search_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.search_tab, text="🔍 Video Search")
        self.setup_search_tab(self.search_tab)
        self.fav_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.fav_tab, text="⭐ Favorites")
        self.setup_saved_tab(self.fav_tab, "⭐ Favorite Channels", "favorites")
        self.history_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.history_tab, text="📋 History")
        self.setup_saved_tab(self.history_tab, "📋 Watch History", "history")

    # ---- IPTV tab
    def setup_iptv_tab(self, parent):
        left = tk.Frame(parent, bg="#0d0d0d", width=430)
        left.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left.pack_propagate(False)
        self.setup_channel_list(left)
        right = tk.Frame(parent, bg="#0d0d0d")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.setup_player(right)

    def setup_channel_list(self, parent):
        h = tk.Frame(parent, bg="#0d0d0d")
        h.pack(fill=tk.X, pady=(0, 4))
        self.channel_count = tk.Label(h, text="📺 0 channels", font=("Segoe UI", 11), fg="#888888", bg="#0d0d0d")
        self.channel_count.pack(side=tk.LEFT)
        tk.Label(h, text="Sort:", font=("Segoe UI", 9), fg="#888888", bg="#0d0d0d").pack(side=tk.LEFT, padx=(12, 2))
        self.sort_var = tk.StringVar(value=self.settings.get("sort", "Name (A→Z)"))
        sm = ttk.Combobox(h, textvariable=self.sort_var, values=SORT_MODES, width=17, state="readonly")
        sm.pack(side=tk.LEFT)
        sm.bind("<<ComboboxSelected>>", self.on_sort_change)

        f2 = tk.Frame(parent, bg="#0d0d0d")
        f2.pack(fill=tk.X, pady=(0, 4))
        tk.Label(f2, text="Category:", font=("Segoe UI", 9), fg="#888888", bg="#0d0d0d").pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value="All")
        self.category_menu = ttk.Combobox(f2, textvariable=self.category_var, values=["All"], width=16, state="readonly")
        self.category_menu.pack(side=tk.LEFT, padx=3)
        self.category_menu.bind("<<ComboboxSelected>>", lambda e: self.display_channels())
        self.status_var = tk.StringVar(value=self.settings.get("status_filter", "All"))
        stf = ttk.Combobox(f2, textvariable=self.status_var, values=STATUS_FILTERS, width=12, state="readonly")
        stf.pack(side=tk.LEFT, padx=3)
        stf.bind("<<ComboboxSelected>>", self.on_status_filter)
        self.pin_var = tk.BooleanVar(value=self.settings.get("pin_favs", True))
        tk.Checkbutton(f2, text="★ on top", variable=self.pin_var, command=self.on_sort_change, bg="#0d0d0d",
                       fg="#bbbbbb", selectcolor="#1a1a1a", activebackground="#0d0d0d",
                       activeforeground="#ffffff").pack(side=tk.LEFT, padx=4)

        self.search_entry = tk.Entry(parent, font=("Segoe UI", 10), bg="#1a1a1a", fg="#666666", bd=0,
                                     insertbackground="#ffffff")
        self.search_entry.pack(fill=tk.X, ipady=6, pady=(0, 4))
        self.search_entry.insert(0, "🔍 Search channels...")
        self.search_entry.bind("<FocusIn>", self.on_search_focus)
        self.search_entry.bind("<FocusOut>", self.on_search_blur)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        lf = tk.Frame(parent, bg="#0d0d0d")
        lf.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(lf, style="Ch.Treeview", columns=("cat", "st"), selectmode="browse")
        self.tree.heading("#0", text="Channel ▲", anchor="w", command=lambda: self.header_sort("name"))
        self.tree.heading("cat", text="Category", anchor="w", command=lambda: self.header_sort("cat"))
        self.tree.heading("st", text="●", anchor="center", command=lambda: self.header_sort("st"))
        self.tree.column("#0", width=230, stretch=True)
        self.tree.column("cat", width=95, stretch=False)
        self.tree.column("st", width=34, stretch=False, anchor="center")
        sb = tk.Scrollbar(lf, orient=tk.VERTICAL, command=self.tree.yview)
        # Keep the vertical scrollbar attached to the channel list at all times.
        self.channel_scrollbar = sb
        self.tree.configure(yscrollcommand=lambda a, b: (sb.set(a, b), self.schedule_logo_load()))
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<Double-1>", self.play_selected)
        self.tree.bind("<Return>", self.play_selected)
        self.tree.bind("<Button-3>", self.show_channel_menu)
        self.tree.bind("<Configure>", lambda e: self.schedule_logo_load())

        self.loading_label = tk.Label(parent, text="⏳ Loading channels...", font=("Segoe UI", 12), fg="#888888",
                                      bg="#0d0d0d")

    # ---- player
    def setup_player(self, parent):
        self.video_slot = tk.Frame(parent, bg="#000000", relief=tk.SUNKEN, bd=2)
        self.video_slot.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        now = tk.Frame(parent, bg="#0d0d0d")
        now.pack(fill=tk.X, pady=5)
        self.now_logo = tk.Label(now, bg="#0d0d0d")
        self.now_logo.pack(side=tk.LEFT, padx=(0, 8))
        self.now_playing = tk.Label(now, text="📺 Ready", font=("Segoe UI", 12), fg="#888888", bg="#0d0d0d")
        self.now_playing.pack(side=tk.LEFT)
        self.live_badge = tk.Label(now, text="", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#0d0d0d", padx=6)
        self.live_badge.pack(side=tk.LEFT, padx=8)
        self.fav_btn = self.btn(now, "☆", self.toggle_favorite, fg="#888888", font=("Segoe UI", 14), padx=8)
        self.fav_btn.pack(side=tk.RIGHT)
        self.fix_btn = self.btn(now, "🔧 Fix link", self.fix_current, padx=8, pady=3)
        self.fix_btn.pack(side=tk.RIGHT, padx=6)

        controls = tk.Frame(parent, bg="#0d0d0d")
        controls.pack(fill=tk.X)
        seek = tk.Frame(controls, bg="#0d0d0d")
        seek.pack(fill=tk.X, pady=(0, 6))
        self.time_label = tk.Label(seek, text="00:00 / 00:00", font=("Segoe UI", 10), fg="#888888", bg="#0d0d0d")
        self.time_label.pack(side=tk.LEFT)
        self.seek_bar = tk.Scale(seek, from_=0, to=1000, orient=tk.HORIZONTAL, showvalue=False, bg="#0d0d0d",
                                 fg="#ff3b30", highlightthickness=0, troughcolor="#2a2a2a", sliderlength=14)
        self.seek_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.seek_bar.bind("<ButtonPress-1>", lambda e: setattr(self, "seeking", True))
        self.seek_bar.bind("<ButtonRelease-1>", self.seek_to)
        vf = tk.Frame(seek, bg="#0d0d0d")
        vf.pack(side=tk.RIGHT)
        self.vol_icon = tk.Label(vf, text="🔊", font=("Segoe UI", 10), fg="#888888", bg="#0d0d0d")
        self.vol_icon.pack(side=tk.LEFT)
        self.vol_bar = tk.Scale(vf, from_=0, to=100, orient=tk.HORIZONTAL, showvalue=False, bg="#0d0d0d", fg="#ff3b30",
                                highlightthickness=0, troughcolor="#2a2a2a", sliderlength=14, length=80,
                                command=lambda v: self.set_volume())
        self.vol_bar.set(self.settings.get("volume", 70))
        self.vol_bar.pack(side=tk.LEFT, padx=5)

        bf = tk.Frame(controls, bg="#0d0d0d")
        bf.pack(pady=6)
        for text, cmd in (("⏮", self.prev_channel), ("⏪", lambda: self.seek_by(-10)), ("▶", self.play_pause),
                          ("⏩", lambda: self.seek_by(10)), ("⏭", self.next_channel), ("⏹", self.stop),
                          ("🔇", self.toggle_mute), ("⛶", self.toggle_fullscreen)):
            b = self.btn(bf, text, cmd, font=("Segoe UI", 20 if text == "▶" else 14), padx=10, pady=5)
            b.pack(side=tk.LEFT, padx=2)
            if text == "▶":
                self.play_btn = b
        tk.Label(parent, text="Space: Play/Pause  |  F or double-click video: Fullscreen  |  PgUp/PgDn: Channel  |  "
                              "↑ ↓: Volume  |  M: Mute  |  Ctrl+L: Links  |  Ctrl+F: Search",
                 font=("Segoe UI", 8), fg="#555555", bg="#0d0d0d").pack(pady=4)

    def build_video_container(self):
        c = self.video_container
        self.video_frame = tk.Frame(c, bg="#000000")
        self.video_frame.pack(fill=tk.BOTH, expand=True)
        self.placeholder = tk.Label(self.video_frame, text="📺\n\nSelect a channel to watch",
                                    font=("Segoe UI", 18), bg="#000000", fg="#444444")
        self.placeholder.place(relx=0.5, rely=0.5, anchor="center")
        # channel name overlay (OSD)
        self.osd = tk.Label(c, text="", font=("Segoe UI", 20, "bold"), fg="#ffffff", bg="#000000", padx=14, pady=8,
                            compound=tk.LEFT)
        # full screen control bar
        self.fs_bar = tk.Frame(c, bg="#111111")
        self.fs_title = tk.Label(self.fs_bar, text="", font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#111111",
                                 compound=tk.LEFT, padx=10)
        self.fs_title.pack(side=tk.LEFT, padx=6, pady=6)
        for text, cmd in (("⛶ Exit", self.exit_fullscreen), ("⏭", self.next_channel), ("⏹", self.stop),
                          ("🔇", self.toggle_mute), ("⏮", self.prev_channel)):
            b = tk.Button(self.fs_bar, text=text, command=cmd, bg="#111111", fg="#ffffff", bd=0, padx=10,
                          font=("Segoe UI", 13), cursor="hand2", activebackground="#333333", activeforeground="#fff")
            b.pack(side=tk.RIGHT, padx=2)
        self.fs_play = tk.Button(self.fs_bar, text="⏸", command=self.play_pause, bg="#111111", fg="#ffffff", bd=0,
                                 padx=12, font=("Segoe UI", 16), cursor="hand2", activebackground="#333333",
                                 activeforeground="#fff")
        self.fs_play.pack(side=tk.RIGHT, padx=2)
        self.fs_hide_job = None
        self.osd_job = None
        for w in (c, self.video_frame, self.placeholder, self.fs_bar, self.osd):
            w.bind("<Motion>", self.on_fs_motion)
            w.bind("<Double-Button-1>", lambda e: self.toggle_fullscreen())
        self.video_frame.bind("<Button-1>", lambda e: self.video_frame.focus_set())

    def place_video(self):
        if self.fullscreen:
            return
        self.video_container.place(in_=self.video_slot, x=0, y=0, relwidth=1, relheight=1)
        self.video_container.lift()

    def on_tab_changed(self, e=None):
        if self.fullscreen:
            return
        if self.tab_control.select() == str(self.iptv_tab):
            self.place_video()
        else:
            self.video_container.place_forget()

    # ---- search tab (as in v3)
    def setup_search_tab(self, parent):
        sf = tk.Frame(parent, bg="#0d0d0d")
        sf.pack(fill=tk.X, pady=10)
        tk.Label(sf, text="🔍 Search Videos:", font=("Segoe UI", 12), fg="#ffffff", bg="#0d0d0d").pack(side=tk.LEFT, padx=10)
        self.video_search_entry = tk.Entry(sf, font=("Segoe UI", 11), bg="#1a1a1a", fg="#ffffff", bd=0,
                                           insertbackground="#ffffff", width=40)
        self.video_search_entry.pack(side=tk.LEFT, padx=10, ipady=6)
        self.video_search_entry.bind("<Return>", self.perform_video_search)
        self.btn(sf, "🔍 Search", self.perform_video_search, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        s2 = tk.Frame(parent, bg="#0d0d0d")
        s2.pack(fill=tk.X, pady=5)
        tk.Label(s2, text="Source:", font=("Segoe UI", 10), fg="#888888", bg="#0d0d0d").pack(side=tk.LEFT, padx=10)
        self.video_source_var = tk.StringVar(value="All")
        sm = ttk.Combobox(s2, textvariable=self.video_source_var, values=["All"] + list(VIDEO_SOURCES.keys()),
                          width=15, state="readonly")
        sm.pack(side=tk.LEFT, padx=5)
        sm.bind("<<ComboboxSelected>>", self.perform_video_search)
        rf = tk.Frame(parent, bg="#0d0d0d")
        rf.pack(fill=tk.BOTH, expand=True, pady=10)
        self.video_results_listbox = tk.Listbox(rf, bg="#1a1a1a", fg="#ffffff", selectbackground="#ff3b30",
                                                selectforeground="#ffffff", font=("Segoe UI", 10), bd=0,
                                                highlightthickness=0)
        sb = tk.Scrollbar(rf, orient=tk.VERTICAL, command=self.video_results_listbox.yview)
        self.video_results_listbox.configure(yscrollcommand=sb.set)
        self.video_results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.video_results_listbox.bind("<Double-1>", self.play_video_search_result)
        self.video_results_listbox.bind("<Return>", self.play_video_search_result)
        self.search_status = tk.Label(parent, text="Enter a search term above", font=("Segoe UI", 9), fg="#666666",
                                      bg="#0d0d0d")
        self.search_status.pack(pady=5)
        self.video_results = []

    # ---- favorites / history tabs
    def setup_saved_tab(self, parent, title, attr):
        h = tk.Frame(parent, bg="#0d0d0d")
        h.pack(fill=tk.X, pady=10)
        tk.Label(h, text=title, font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#0d0d0d").pack(side=tk.LEFT, padx=10)
        self.btn(h, "🗑️ Clear All", lambda: self.clear_saved(attr), fg="#ff3b30", padx=12, pady=5).pack(side=tk.RIGHT, padx=10)
        lb = tk.Listbox(parent, bg="#1a1a1a", fg="#ffffff", selectbackground="#ff3b30", selectforeground="#ffffff",
                        font=("Segoe UI", 11), bd=0, highlightthickness=0)
        sb = tk.Scrollbar(parent, orient=tk.VERTICAL, command=lb.yview)
        lb.configure(yscrollcommand=sb.set)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        sb.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        lb.bind("<Double-1>", lambda e, a=attr: self.play_saved(a))
        lb.bind("<Return>", lambda e, a=attr: self.play_saved(a))
        lb.bind("<Delete>", lambda e, a=attr: self.remove_saved(a))
        setattr(self, attr + "_listbox", lb)
        self.refresh_saved_list(attr)

    # ---------------------------------------------------------------- shortcuts
    def typing(self):
        w = self.root.focus_get()
        return isinstance(w, (tk.Entry, ttk.Entry, ttk.Combobox, tk.Spinbox))

    def key(self, seq, fn, always=False):
        self.root.bind(seq, lambda e: None if (self.typing() and not always) else fn())

    def setup_shortcuts(self):
        self.key("<space>", self.play_pause)
        self.key("<Right>", self.on_right)
        self.key("<Left>", self.on_left)
        self.key("<Up>", lambda: self.volume_step(10))
        self.key("<Down>", lambda: self.volume_step(-10))
        self.key("<Prior>", self.prev_channel)
        self.key("<Next>", self.next_channel)
        self.key("<m>", self.toggle_mute)
        self.key("<f>", self.toggle_fullscreen)
        self.key("<F11>", self.toggle_fullscreen, always=True)
        self.key("<Escape>", self.exit_fullscreen, always=True)
        self.key("<Control-l>", self.toggle_link_visibility, always=True)
        self.key("<Control-r>", lambda: self.load_source(self.source_var.get(), silent=True), always=True)
        self.key("<Control-f>", self.focus_search, always=True)

    def on_right(self):
        (self.next_channel if (self.fullscreen and self.cur_is_live) else (lambda: self.seek_by(5)))()

    def on_left(self):
        (self.prev_channel if (self.fullscreen and self.cur_is_live) else (lambda: self.seek_by(-5)))()

    # ================================================================ SOURCES / LOADING
    def load_selected_source(self):
        name = self.source_var.get()
        if name in self.all_sources():
            self.settings["last_source"] = name
            self.save_all()
            self.load_source(name)

    def add_custom_source(self):
        url = simpledialog.askstring("Add playlist", "M3U / M3U8 playlist URL:")
        if not url or "://" not in url:
            return
        name = simpledialog.askstring("Name", "Name for this source:", initialvalue=url.rsplit("/", 1)[-1][:30]) or url[:30]
        self.settings.setdefault("custom_sources", []).append({"name": name, "url": url.strip()})
        self.save_all()
        self.source_menu["values"] = list(self.all_sources().keys())
        self.source_var.set(f"⭐ {name}")
        self.load_selected_source()

    def open_m3u_file(self):
        path = filedialog.askopenfilename(title="Open playlist", filetypes=[("Playlists", "*.m3u *.m3u8 *.txt"), ("All", "*.*")])
        if not path:
            return
        try:
            text = Path(path).read_text(encoding="utf-8", errors="ignore")
        except OSError as e:
            self.show_error(str(e))
            return
        chans = merge_playlists([parse_m3u(text, "file")], self.overrides)
        self.loading_gen += 1
        self.finish_load(self.loading_gen, chans, False, [], f"📂 {Path(path).name}")

    def load_source(self, name, silent=False):
        src = self.all_sources().get(name)
        if not src:
            return
        self.loading_gen += 1
        gen = self.loading_gen
        if not silent or not self.channels:
            self.loading_label.pack(fill=tk.X)
            self.source_status.config(text="⏳ Loading...")
        else:
            self.source_status.config(text="🔄 Updating...")
        self.set_status(f"{'Updating' if silent else 'Loading'} {name}...")
        threading.Thread(target=self.fetch_source, args=(gen, name, src["urls"], silent), daemon=True).start()

    def fetch_text(self, url, conditional):
        if requests is None:
            raise RuntimeError("The requests package is required to load online playlists.")
        headers = dict(UA)
        cached = self.http_cache.get(url)
        if conditional and cached:
            if cached.get("etag"):
                headers["If-None-Match"] = cached["etag"]
            if cached.get("lm"):
                headers["If-Modified-Since"] = cached["lm"]
        r = requests.get(url, headers=headers, timeout=40)
        if r.status_code == 304 and cached:
            return cached["text"], False
        r.raise_for_status()
        r.encoding = r.encoding or "utf-8"
        text = r.content.decode("utf-8", errors="ignore")
        self.http_cache[url] = {"etag": r.headers.get("ETag"), "lm": r.headers.get("Last-Modified"), "text": text}
        return text, True

    def fetch_source(self, gen, name, urls, silent):
        lists, errors = [], []

        def one(u):
            text, changed = self.fetch_text(u, silent)
            return parse_m3u(text, u)

        with ThreadPoolExecutor(max_workers=6) as ex:
            futs = {ex.submit(one, u): u for u in urls}
            order = {u: i for i, u in enumerate(urls)}
            res = {}
            for f in as_completed(futs):
                u = futs[f]
                try:
                    res[order[u]] = f.result()
                except Exception as e:
                    errors.append(f"{name}: {type(e).__name__}")
        for i in sorted(res):
            lists.append(res[i])
        chans = merge_playlists(lists, self.overrides)
        self.call_ui(self.finish_load, gen, chans, silent, errors, name)

    def finish_load(self, gen, chans, silent, errors, name):
        if gen != self.loading_gen:
            return
        self.loading_label.pack_forget()
        if not chans:
            self.source_status.config(text="❌ Failed")
            if not silent:
                self.show_error("No channels found.\n" + "\n".join(errors[:3]))
            else:
                self.set_status("Update failed: " + (errors[0] if errors else "empty playlist"))
            return
        added = removed = 0
        if silent and self.channels:
            old = {c["url"]: c for c in self.channels}
            for c in chans:
                o = old.get(c["url"])
                if o:
                    c["working"], c["checked"] = o.get("working"), o.get("checked", 0)
            new_urls = {c["url"] for c in chans}
            added = sum(1 for c in chans if c["url"] not in old)
            removed = sum(1 for u in old if u not in new_urls)
        self.channels = chans
        if self.current is not None:      # keep pointing at the same channel after a refresh
            same = next((c for c in chans if c["url"] == self.current.get("url")), None)
            if same is not None:
                self.current = same
        self.categories = {}
        for c in chans:
            self.categories.setdefault(c["category"], []).append(c)
        self.repairer.add(chans)
        cats = ["All"] + sorted(self.categories.keys(), key=natural_key)
        keep = self.category_var.get()
        self.category_menu["values"] = cats
        self.category_var.set(keep if keep in cats else "All")
        self.last_update = datetime.now()
        self.update_label.config(text=f"🕒 Updated {self.last_update:%H:%M:%S}" +
                                 (f"   +{added} new  −{removed} removed" if silent else ""))
        self.source_status.config(text=f"✅ {len(chans):,} channels" + (f"  ({len(errors)} list(s) failed)" if errors else ""))
        self.set_status(f"Loaded {len(chans):,} channels from {name}" +
                        (f" — {added} new, {removed} removed" if silent else ""))
        self.display_channels()
        self.start_validation()

    def on_live_toggle(self, e=None):
        self.settings["live_update"] = bool(self.live_var.get())
        self.settings["auto_fix"] = bool(self.fix_var.get())
        try:
            self.settings["refresh_minutes"] = int(self.refresh_var.get())
        except ValueError:
            pass
        self.save_all()

    def live_update_check(self):
        try:
            if self.settings.get("live_update") and self.last_update and not self.is_closing:
                age = (datetime.now() - self.last_update).total_seconds() / 60
                if age >= self.settings.get("refresh_minutes", 30):
                    self.load_source(self.source_var.get(), silent=True)
        finally:
            if not self.is_closing:
                self.root.after(60000, self.live_update_check)

    # ================================================================ LIST / SORT / FILTER
    def query(self):
        q = self.search_entry.get().strip()
        return "" if q.startswith("🔍") else q

    def current_filtered(self):
        chans = filter_channels(self.channels, self.category_var.get(), self.query(), self.status_var.get())
        return sort_channels(chans, self.sort_var.get(), self.favorites, [h["url"] for h in self.history],
                             self.pin_var.get())

    def status_icon(self, ch):
        return "✅" if ch.get("working") is True else ("❌" if ch.get("working") is False else "·")

    def display_channels(self):
        self.display_gen += 1
        gen = self.display_gen
        keep_url = self.current["url"] if self.current else None
        self.view = self.current_filtered()
        previous_scroll = self.tree.yview()[0] if self.tree.get_children() else 0
        self.tree.delete(*self.tree.get_children())
        self.by_iid = {}
        self.channel_count.config(text=f"📺 {len(self.view):,} / {len(self.channels):,}")
        self.update_headings()
        self._insert_chunk(gen, 0, keep_url)
        # Restore the position when health checks filter out stopped rows.
        if previous_scroll and not keep_url:
            self.root.after(80, lambda: self.tree.yview_moveto(previous_scroll) if gen == self.display_gen else None)

    def _insert_chunk(self, gen, start, keep_url):
        if gen != self.display_gen:
            return
        end = min(start + 400, len(self.view))
        for ch in self.view[start:end]:
            iid = str(ch["_i"])
            self.by_iid[iid] = ch
            fav = "★ " if is_favorite(ch, self.favorites) else ""
            kw = {"image": self.cached_logo(ch)} if PIL_OK else {}
            self.tree.insert("", "end", iid=iid, text=f" {fav}{ch['name']}", values=(ch.get("category", ""), self.status_icon(ch)), **kw)
            if keep_url and ch["url"] == keep_url:
                try:
                    self.tree.selection_set(iid)
                    self.tree.see(iid)
                except Exception:
                    pass
        if end < len(self.view):
            self.root.after(5, self._insert_chunk, gen, end, keep_url)
        else:
            self.schedule_logo_load()

    def update_headings(self):
        mode = self.sort_var.get()
        self.tree.heading("#0", text="Channel" + (" ▲" if mode == "Name (A→Z)" else " ▼" if mode == "Name (Z→A)" else ""))
        self.tree.heading("cat", text="Category" + (" ▲" if mode == "Category → Name" else ""))
        self.tree.heading("st", text="●" + ("▲" if mode == "Working first" else ""))

    def header_sort(self, col):
        cur = self.sort_var.get()
        if col == "name":
            self.sort_var.set("Name (Z→A)" if cur == "Name (A→Z)" else "Name (A→Z)")
        elif col == "cat":
            self.sort_var.set("Category → Name")
        else:
            self.sort_var.set("Working first")
        self.on_sort_change()

    def on_sort_change(self, e=None):
        self.settings["sort"] = self.sort_var.get()
        self.settings["pin_favs"] = bool(self.pin_var.get())
        self.display_channels()

    def on_status_filter(self, e=None):
        self.settings["status_filter"] = self.status_var.get()
        self.display_channels()

    def on_search_focus(self, e):
        if self.search_entry.get().startswith("🔍"):
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="#ffffff")

    def on_search_blur(self, e):
        if not self.search_entry.get():
            self.search_entry.insert(0, "🔍 Search channels...")
            self.search_entry.config(fg="#666666")

    def on_search(self, e=None):
        if getattr(self, "_search_job", None):
            self.root.after_cancel(self._search_job)
        self._search_job = self.root.after(180, self.display_channels)

    def focus_search(self):
        self.search_entry.focus_set()

    # ================================================================ LOGOS
    def default_photo(self):
        if self.default_icon is None and PIL_OK:
            img = Image.new("RGBA", (self.LOGO, self.LOGO), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            d.rounded_rectangle((1, 5, self.LOGO - 2, self.LOGO - 6), radius=4, outline=(110, 110, 110, 255), width=2)
            d.line((self.LOGO // 2 - 5, 2, self.LOGO // 2, 5), fill=(110, 110, 110, 255), width=2)
            d.line((self.LOGO // 2 + 5, 2, self.LOGO // 2, 5), fill=(110, 110, 110, 255), width=2)
            self.default_icon = ImageTk.PhotoImage(img)
        return self.default_icon

    def cached_logo(self, ch, size=None):
        size = size or self.LOGO
        return self.logo_img.get((ch.get("logo") or ch["name"], size)) or self.default_photo()

    def schedule_logo_load(self):
        if not PIL_OK:
            return
        if getattr(self, "_logo_job", None):
            self.root.after_cancel(self._logo_job)
        self._logo_job = self.root.after(120, self.load_visible_logos)

    def load_visible_logos(self):
        n = len(self.view)
        if not n:
            return
        a, b = self.tree.yview()
        first = max(0, int(a * n) - 8)
        shown = max(1, int(self.tree.winfo_height() / self.ROW_H))
        last = min(n, first + shown + 24)
        for ch in self.view[first:last]:
            key = (ch.get("logo") or ch["name"], self.LOGO)
            if key in self.logo_img or key in self.logo_req:
                continue
            self.logo_req.add(key)
            self.logo_pool.submit(self.logo_worker, ch["name"], ch.get("logo", ""), self.LOGO, key, str(ch["_i"]))

    def logo_worker(self, name, url, size, key, iid):
        img = self.logos.load(url, size) if url else None
        if img is None:
            img = LogoStore.placeholder(name, size)
        self.call_ui(self.apply_logo, key, img, iid)

    def apply_logo(self, key, img, iid):
        self.logo_req.discard(key)
        if img is None or self.is_closing:
            return
        photo = ImageTk.PhotoImage(img)
        self.logo_img[key] = photo
        # every visible row that shares this logo/name gets it
        if self.tree.exists(iid):
            self.tree.item(iid, image=photo)
        ch = self.by_iid.get(iid)
        if ch is not None and key[0] == (ch.get("logo") or ch["name"]):
            for other_iid, other in self.by_iid.items():
                if other_iid != iid and (other.get("logo") or other["name"]) == key[0] and self.tree.exists(other_iid):
                    self.tree.item(other_iid, image=photo)

    def set_now_logo(self, ch):
        if not PIL_OK:
            return
        key = (ch.get("logo") or ch["name"], 48)

        def work():
            img = (self.logos.load(ch.get("logo", ""), 48) if ch.get("logo") else None) or LogoStore.placeholder(ch["name"], 48)
            self.call_ui(show, img)

        def show(img):
            if self.current is not ch or img is None:
                return
            photo = ImageTk.PhotoImage(img)
            self.logo_img[key] = photo
            self.now_logo.config(image=photo)
            self.fs_title.config(image=photo)
            self.osd.config(image=photo)

        if key in self.logo_img:
            for w in (self.now_logo, self.fs_title, self.osd):
                w.config(image=self.logo_img[key])
        else:
            self.logo_pool.submit(work)

    # ================================================================ LINK VALIDATION
    def start_validation(self, force=False):
        self.val_gen += 1
        gen = self.val_gen
        if self.val_pool:
            self.val_pool.shutdown(wait=False, cancel_futures=True)
        todo = [c for c in self.view if force or c.get("working") is None]
        seen = {id(c) for c in todo}
        todo += [c for c in self.channels if id(c) not in seen and (force or c.get("working") is None)]
        self.val_total, self.val_done = len(todo), 0
        if not todo:
            self.link_count_label.config(text=f"🔗 all {len(self.channels):,} checked")
            return
        self.val_pool = ThreadPoolExecutor(max_workers=24)
        for c in todo:
            self.val_pool.submit(self.val_task, c, gen)
        self.root.after(400, self.flush_validation, gen)

    def val_task(self, ch, gen):
        if gen != self.val_gen or self.is_closing:
            return
        ok = check_stream(ch["url"], ch.get("opts", []))
        with self.val_lock:
            self.val_buf.append((ch, ok, gen))

    def flush_validation(self, gen):
        if gen != self.val_gen or self.is_closing:
            return
        with self.val_lock:
            batch, self.val_buf = self.val_buf, []
        for ch, ok, g in batch:
            if g != gen:
                continue
            ch["working"], ch["checked"] = ok, time.time()
            self.val_done += 1
            iid = str(ch["_i"])
            if self.tree.exists(iid):
                self.tree.set(iid, "st", self.status_icon(ch))
        good = sum(1 for c in self.channels if c.get("working") is True)
        bad = sum(1 for c in self.channels if c.get("working") is False)
        self.link_count_label.config(text=f"🔗 {self.val_done}/{self.val_total} checked   ✅ {good:,}   ❌ {bad:,}")
        if (batch and self.status_var.get() in ("Hide dead", "Dead only", "Working only")
                and time.monotonic() - self._last_filter_redraw >= 4):
            self._last_filter_redraw = time.monotonic()
            self.display_channels()
        if self.val_done < self.val_total:
            self.root.after(400, self.flush_validation, gen)
        elif self.sort_var.get() == "Working first" or self.status_var.get() != "All":
            self.display_channels()

    def recheck_loop(self):
        """Every few minutes: give dead links another chance and refresh stale 'working' marks."""
        try:
            if self.channels and not self.is_closing and self.val_done >= self.val_total:
                now = time.time()
                stale = [c for c in self.channels if c.get("working") is False or now - c.get("checked", 0) > 1800][:300]
                for c in stale:
                    c["working"] = None
                if stale:
                    self.start_validation()
        finally:
            if not self.is_closing:
                self.root.after(5 * 60000, self.recheck_loop)

    # ================================================================ LINK REPAIR
    def fix_current(self):
        if self.current:
            self.repair_channel(self.current, auto_play=True, manual=True)
        else:
            self.set_status("Play or select a channel first")

    def fix_selected(self):
        ch = self.selected_channel()
        if ch:
            self.repair_channel(ch, auto_play=False, manual=True)

    def repair_channel(self, ch, auto_play=True, manual=False):
        self.set_status(f"🔧 Looking for a working link for {ch['name']}...")
        dead = {c["url"] for c in self.channels if c.get("working") is False}

        def work():
            found = self.repairer.find_working(ch, exclude=dead)
            self.call_ui(done, found)

        def done(found):
            if not found:
                ch["working"] = False
                self.set_status(f"❌ No working replacement found for {ch['name']}")
                if manual:
                    messagebox.showinfo("Fix link", f"No working alternative found for\n{ch['name']}.\n\n"
                                                    "Try loading a bigger source (MEGA pack) so more candidates exist.")
                return
            self.apply_fix(ch, found)
            self.set_status(f"✅ Fixed {ch['name']} — new link works")
            if auto_play and self.current is ch:
                self.play_channel(ch)

        threading.Thread(target=work, daemon=True).start()

    def apply_fix(self, ch, found):
        old = ch["url"]
        ch["url"] = found["url"]
        ch["opts"] = found.get("opts", [])
        ch["working"], ch["checked"] = True, time.time()
        if found.get("logo") and not ch.get("logo"):
            ch["logo"] = found["logo"]
        self.overrides[old] = found["url"]
        jsave(APP_DIR / "link_overrides.json", self.overrides)
        iid = str(ch.get("_i", ""))
        if self.tree.exists(iid):
            self.tree.set(iid, "st", "✅")

    def fix_all_dead(self):
        dead = [c for c in self.channels if c.get("working") is False]
        if not dead:
            messagebox.showinfo("Fix dead links", "No dead links found yet. Wait for the link check to finish.")
            return
        if not messagebox.askyesno("Fix dead links", f"Try to find replacements for {len(dead)} dead channels?\n"
                                                      "This runs in the background."):
            return
        dead = dead[:300]
        deadset = {c["url"] for c in self.channels if c.get("working") is False}

        def work():
            fixed = 0
            for i, ch in enumerate(dead, 1):
                if self.is_closing:
                    return
                found = self.repairer.find_working(ch, exclude=deadset, workers=6)
                if found:
                    fixed += 1
                    self.call_ui(self.apply_fix, ch, found)
                self.call_ui(self.set_status, f"🔧 Fixing dead links {i}/{len(dead)} — {fixed} fixed")
            self.call_ui(self.set_status, f"🔧 Done: fixed {fixed} of {len(dead)} dead links")
            self.call_ui(self.display_channels)

        threading.Thread(target=work, daemon=True).start()

    # ================================================================ PLAYBACK
    def selected_channel(self):
        sel = self.tree.selection()
        return self.by_iid.get(sel[0]) if sel else None

    def play_selected(self, event=None):
        ch = self.selected_channel()
        if not ch:
            return
        if ch.get("working") is False:
            ans = messagebox.askyesnocancel("Dead link", "This link looks dead.\n\nYes = find a working replacement\n"
                                                         "No = try to play it anyway")
            if ans is None:
                return
            if ans:
                self.current = ch
                self.repair_channel(ch, auto_play=True)
                return
        self.play_channel(ch)

    def play_channel(self, ch):
        """ch: dict with at least name + url (opts/logo optional)."""
        try:
            ch.setdefault("opts", [])
            self.current = ch
            self.placeholder.place_forget()
            media = self.instance.media_new(ch["url"])
            for o in ch["opts"]:
                try:
                    media.add_option(o)
                except Exception:
                    pass
            self.player.set_media(media)
            if sys.platform == "win32":
                self.player.set_hwnd(self.video_frame.winfo_id())
            elif sys.platform == "darwin":
                self.player.set_nsobject(self.video_frame.winfo_id())
            else:
                self.player.set_xwindow(self.video_frame.winfo_id())
            self.player.audio_set_volume(int(self.vol_bar.get()))
            self.player.play()
            self.is_playing, self.is_paused = True, False
            self.play_started, self.seen_playing, self.cur_is_live = time.time(), False, False
            self.fix_attempted = False
            self.play_btn.config(text="⏸")
            self.fs_play.config(text="⏸")
            self.now_playing.config(text=f"▶ {ch['name']}", fg="#ffffff")
            self.live_badge.config(text="", bg="#0d0d0d")
            self.set_now_logo(ch)
            self.fs_title.config(text=ch["name"])
            self.show_osd(ch["name"])
            self.add_history(ch)
            self.update_fav_button()
            self.set_status(f"Playing: {ch['name']}" + (f" | URL: {ch['url']}" if self.is_authenticated else ""))
        except Exception as e:
            self.show_error(f"Could not start playback ({type(e).__name__}).")

    def play_pause(self):
        if not self.is_playing:
            ch = self.selected_channel() or (self.view[0] if self.view else None)
            if ch is None:
                self.show_error("No channels loaded")
                return
            self.play_channel(ch)
            return
        if self.is_paused:
            self.player.play()
            self.is_paused = False
        else:
            self.player.pause()
            self.is_paused = True
        sym = "▶" if self.is_paused else "⏸"
        self.play_btn.config(text=sym)
        self.fs_play.config(text=sym)

    def stop(self):
        self.player.stop()
        self.is_playing = self.is_paused = False
        self.current = None
        self.play_btn.config(text="▶")
        self.now_playing.config(text="⏹ Stopped", fg="#888888")
        self.now_logo.config(image="")
        self.live_badge.config(text="", bg="#0d0d0d")
        self.placeholder.place(relx=0.5, rely=0.5, anchor="center")
        self.set_status("Stopped")

    def step_channel(self, delta):
        if not self.view:
            return
        pos = -1
        if self.current is not None:
            for i, c in enumerate(self.view):
                if c is self.current:
                    pos = i
                    break
        if pos < 0:
            sel = self.tree.selection()
            pos = self.view.index(self.by_iid[sel[0]]) if sel and sel[0] in self.by_iid else (-1 if delta > 0 else 0)
        n = len(self.view)
        for _ in range(min(n, 25)):              # skip known-dead channels
            pos = (pos + delta) % n
            if self.view[pos].get("working") is not False:
                break
        ch = self.view[pos]
        iid = str(ch["_i"])
        if self.tree.exists(iid):
            self.tree.selection_set(iid)
            self.tree.see(iid)
        self.play_channel(ch)

    def prev_channel(self):
        self.step_channel(-1)

    def next_channel(self):
        self.step_channel(1)

    def seek_by(self, secs):
        if self.is_playing and self.player.get_length() > 0:
            self.player.set_time(max(0, self.player.get_time() + secs * 1000))

    def seek_to(self, e):
        self.seeking = False
        if self.is_playing and self.player.get_length() > 0:
            self.player.set_position(self.seek_bar.get() / 1000.0)

    def toggle_mute(self):
        self.player.audio_toggle_mute()
        self.vol_icon.config(text="🔇" if self.player.audio_get_mute() else "🔊")

    def set_volume(self):
        vol = int(self.vol_bar.get())
        self.player.audio_set_volume(vol)
        self.settings["volume"] = vol

    def volume_step(self, d):
        self.vol_bar.set(max(0, min(100, int(self.vol_bar.get()) + d)))
        self.set_volume()
        if self.fullscreen:
            self.show_osd(f"🔊 {int(self.vol_bar.get())}%", plain=True)

    def tick(self):
        """Twice a second: time/seek display, LIVE badge, stream failure detection."""
        try:
            if self.is_playing and self.current is not None and not self.is_closing:
                st = self.player.get_state()
                elapsed = time.time() - self.play_started
                if st == vlc.State.Playing:
                    if not self.seen_playing:
                        self.seen_playing = True
                        self.current["working"] = True
                        iid = str(self.current.get("_i", ""))
                        if self.tree.exists(iid):
                            self.tree.set(iid, "st", "✅")
                    length, t = self.player.get_length(), self.player.get_time()
                    if length > 0:
                        self.cur_is_live = False
                        self.live_badge.config(text="", bg="#0d0d0d")
                        self.time_label.config(text=f"{fmt_time(t)} / {fmt_time(length)}")
                        if not self.seeking:
                            self.seek_bar.set(int(1000 * t / max(1, length)))
                    else:
                        self.cur_is_live = True
                        self.live_badge.config(text="● LIVE", bg="#ff3b30")
                        self.time_label.config(text=f"{fmt_time(t)}")
                        if not self.seeking:
                            self.seek_bar.set(1000)
                elif st == vlc.State.Error or (st == vlc.State.Ended and (not self.seen_playing or self.cur_is_live)) \
                        or (not self.seen_playing and elapsed > 25 and st in (vlc.State.Opening, vlc.State.NothingSpecial)):
                    self.on_stream_failure()
        except Exception as e:
            print("tick:", e)
        finally:
            if not self.is_closing:
                self.root.after(500, self.tick)

    def on_stream_failure(self):
        ch = self.current
        if ch is None or self.fix_attempted:
            return
        self.fix_attempted = True
        ch["working"] = False
        iid = str(ch.get("_i", ""))
        if self.tree.exists(iid):
            self.tree.set(iid, "st", "❌")
        self.live_badge.config(text="✖ BROKEN", bg="#7a1d16")
        if self.settings.get("auto_fix", True) and "_i" in ch:
            self.set_status(f"⚠ {ch['name']} stopped working — searching for a replacement link...")
            self.repair_channel(ch, auto_play=True)
        else:
            self.set_status(f"⚠ {ch['name']} could not be played")

    # ================================================================ FULL SCREEN
    def toggle_fullscreen(self):
        if self.fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()

    def enter_fullscreen(self):
        if self.fullscreen:
            return
        self.fullscreen = True
        self.root.attributes("-fullscreen", True)
        self.main_frame.pack_forget()
        self.status.pack_forget()
        self.video_container.place_forget()
        self.video_container.place(x=0, y=0, relwidth=1, relheight=1)
        self.video_container.lift()
        if self.current:
            self.show_osd(self.current["name"])
        self.show_fs_bar()

    def exit_fullscreen(self):
        if not self.fullscreen:
            return
        self.fullscreen = False
        if self.fs_hide_job:
            self.root.after_cancel(self.fs_hide_job)
        self.fs_bar.place_forget()
        self.osd.place_forget()
        self.video_container.config(cursor="")
        self.root.attributes("-fullscreen", False)
        self.video_container.place_forget()
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.root.after(50, self.on_tab_changed)

    def on_fs_motion(self, e=None):
        if self.fullscreen:
            self.show_fs_bar()

    def show_fs_bar(self):
        self.fs_bar.place(relx=0, rely=1.0, relwidth=1, anchor="sw")
        self.fs_bar.lift()
        self.video_container.config(cursor="")
        if self.fs_hide_job:
            self.root.after_cancel(self.fs_hide_job)
        self.fs_hide_job = self.root.after(3000, self.hide_fs_bar)

    def hide_fs_bar(self):
        if self.fullscreen:
            self.fs_bar.place_forget()
            self.video_container.config(cursor="none")

    def show_osd(self, text, plain=False):
        """Channel name overlay (top-left), visible 4s, full screen only."""
        if not self.fullscreen:
            return
        self.osd.config(text=text, image="" if plain else self.osd.cget("image"))
        self.osd.place(x=20, y=20)
        self.osd.lift()
        if self.osd_job:
            self.root.after_cancel(self.osd_job)
        self.osd_job = self.root.after(4000, self.osd.place_forget)

    # ================================================================ FAVORITES / HISTORY
    @staticmethod
    def entry_for(ch):
        return {"name": ch["name"], "url": ch.get("url", ""), "logo": ch.get("logo", ""), "tvg_id": ch.get("tvg_id", "")}

    def toggle_favorite(self):
        if not self.current:
            return
        ch = self.current
        self.toggle_favorite_ch(ch)
        self.update_fav_button()

    def toggle_favorite_ch(self, ch):
        existing = next((f for f in self.favorites if (f.get("url") and f["url"] == ch.get("url")) or
                         (f.get("tvg_id") and f["tvg_id"] == ch.get("tvg_id")) or
                         (not f.get("url") and f["name"] == ch["name"])), None)
        if existing:
            self.favorites.remove(existing)
        else:
            self.favorites.append(self.entry_for(ch))
        jsave(APP_DIR / "favorites.json", self.favorites)
        self.refresh_saved_list("favorites")
        self.display_channels()

    def update_fav_button(self):
        fav = self.current is not None and is_favorite(self.current, self.favorites)
        self.fav_btn.config(text="★" if fav else "☆", fg="#ff3b30" if fav else "#888888")

    def add_history(self, ch):
        self.history = [h for h in self.history if h.get("url") != ch.get("url")]
        self.history.insert(0, self.entry_for(ch))
        del self.history[100:]
        jsave(APP_DIR / "history.json", self.history)
        self.refresh_saved_list("history")

    def refresh_saved_list(self, attr):
        lb = getattr(self, attr + "_listbox")
        lb.delete(0, tk.END)
        for it in getattr(self, attr)[:100]:
            lb.insert(tk.END, it["name"])

    def play_saved(self, attr):
        lb = getattr(self, attr + "_listbox")
        sel = lb.curselection()
        if not sel:
            return
        it = getattr(self, attr)[sel[0]]
        ch = next((c for c in self.channels if (it.get("url") and c["url"] == it["url"]) or
                   (it.get("tvg_id") and c.get("tvg_id") == it["tvg_id"]) or c["name"] == it["name"]), None)
        if ch is None and it.get("url"):
            ch = dict(it, opts=[])
        if ch is None:
            self.show_error(f"'{it['name']}' is not in the loaded playlist. Load its source first.")
            return
        self.tab_control.select(self.iptv_tab)
        self.play_channel(ch)

    def remove_saved(self, attr):
        lb = getattr(self, attr + "_listbox")
        sel = lb.curselection()
        if sel:
            del getattr(self, attr)[sel[0]]
            jsave(APP_DIR / (attr + ".json"), getattr(self, attr))
            self.refresh_saved_list(attr)
            self.display_channels()

    def clear_saved(self, attr):
        if messagebox.askyesno("Clear", f"Remove all {attr}?"):
            setattr(self, attr, [])
            jsave(APP_DIR / (attr + ".json"), [])
            self.refresh_saved_list(attr)
            self.display_channels()

    # ================================================================ VIDEO SEARCH (as in v3)
    def perform_video_search(self, event=None):
        query = self.video_search_entry.get().strip()
        if not query:
            self.search_status.config(text="Please enter a search term")
            return
        if requests is None or BeautifulSoup is None:
            self.search_status.config(text="Install 'requests' and 'beautifulsoup4' for video search")
            return
        self.video_results_listbox.delete(0, tk.END)
        self.search_status.config(text=f"🔍 Searching for: {query}...")
        self.video_results = []
        threading.Thread(target=self.search_all_sources, args=(query,), daemon=True).start()

    def search_all_sources(self, query):
        flt = self.video_source_var.get()
        results = []
        for name, info in VIDEO_SOURCES.items():
            if flt != "All" and flt != name:
                continue
            try:
                url = info["url"] + info["search"].format(query=urllib.parse.quote(query))
                r = requests.get(url, headers=UA, timeout=15)
                if r.status_code != 200:
                    continue
                soup = BeautifulSoup(r.text, "html.parser")
                found = 0
                for a in soup.find_all("a", href=True):
                    href, text = a.get("href", ""), a.get_text(strip=True)
                    if href and any(k in href for k in (".mp4", "/watch", "/video", "/movie")) and 5 < len(text) < 100:
                        results.append({"title": text[:80], "url": href if href.startswith("http") else info["url"] + href,
                                        "source": name})
                        found += 1
                        if found >= 15:
                            break
            except Exception as e:
                print(f"Error searching {name}: {e}")
        self.call_ui(self.update_video_results, results)

    def update_video_results(self, results):
        self.video_results_listbox.delete(0, tk.END)
        self.video_results = results
        if not results:
            self.search_status.config(text="No results found")
            return
        for r in results:
            self.video_results_listbox.insert(tk.END, f"[{r['source']}] {r['title']}")
        self.search_status.config(text=f"Found {len(results)} results")

    def play_video_search_result(self, event=None):
        sel = self.video_results_listbox.curselection()
        if sel and 0 <= sel[0] < len(self.video_results):
            r = self.video_results[sel[0]]
            self.tab_control.select(self.iptv_tab)
            self.play_channel({"name": r["title"], "url": r["url"], "logo": "", "opts": []})

    # ================================================================ MENU / INFO / LINKS
    def toggle_link_visibility(self):
        if self.is_authenticated:
            self.is_authenticated = False
            self.link_btn.config(text="🔒 Links Hidden", fg="#ff3b30")
            self.set_status("Links hidden")
            return
        pw = simpledialog.askstring("Private links", "Enter access code:", show="*")
        if pw is not None and hashlib.sha256(pw.encode()).hexdigest() == PASSWORD_HASH:
            self.is_authenticated = True
            if self.links_relock_job:
                self.root.after_cancel(self.links_relock_job)
            self.links_relock_job = self.root.after(5 * 60000, self.relock_links)
            self.link_btn.config(text="🔓 Links Visible", fg="#00ff00")
            self.set_status("Links visible temporarily")
        elif pw is not None:
            messagebox.showerror("Access Denied", "Incorrect password!")

    def relock_links(self):
        self.is_authenticated = False
        self.links_relock_job = None
        self.link_btn.config(text="🔒 Links Hidden", fg="#ff3b30")

    def show_channel_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        m = tk.Menu(self.root, tearoff=0, bg="#1a1a1a", fg="#ffffff")
        m.add_command(label="▶ Play", command=self.play_selected)
        m.add_command(label="🔧 Fix broken link", command=self.fix_selected)
        m.add_command(label="🔎 Re-check this link", command=self.recheck_selected)
        m.add_command(label="⭐ Add/Remove Favorite", command=lambda: self.toggle_favorite_ch(self.by_iid[iid]))
        m.add_command(label="📋 Copy URL", command=self.copy_channel_url)
        m.add_command(label="ℹ️ Info", command=self.show_channel_info)
        m.post(event.x_root, event.y_root)

    def recheck_selected(self):
        ch = self.selected_channel()
        if not ch:
            return

        def work():
            ok = check_stream(ch["url"], ch.get("opts", []))
            self.call_ui(done, ok)

        def done(ok):
            ch["working"], ch["checked"] = ok, time.time()
            iid = str(ch["_i"])
            if self.tree.exists(iid):
                self.tree.set(iid, "st", self.status_icon(ch))
            self.set_status(f"{ch['name']}: {'✅ working' if ok else '❌ not working'}")

        threading.Thread(target=work, daemon=True).start()

    def copy_channel_url(self):
        if not self.is_authenticated:
            messagebox.showwarning("Access Denied", "Enter password first (Ctrl+L)")
            return
        ch = self.selected_channel()
        if ch:
            self.root.clipboard_clear()
            self.root.clipboard_append(ch["url"])
            self.set_status("✅ URL copied to clipboard")

    def show_channel_info(self):
        ch = self.selected_channel()
        if not ch:
            return
        w = ch.get("working")
        info = (f"Channel: {ch['name']}\nCategory: {ch.get('category', '?')}\n"
                f"Quality: {str(ch['quality']) + 'p' if ch.get('quality') else 'unknown'}\n"
                f"Status: {'✅ Working' if w else '❌ Dead' if w is False else '⏳ Unchecked'}\n"
                f"Alternative links known: {len(ch.get('alts', []))}\n")
        info += f"URL: {ch['url']}\n" if self.is_authenticated else "URL: 🔒 Hidden (Ctrl+L to reveal)\n"
        messagebox.showinfo("Channel Info", info)

    # ================================================================ UTIL
    def show_error(self, message):
        self.set_status(f"Error: {message}".splitlines()[0])
        self.loading_label.pack_forget()
        messagebox.showerror("Error", message)

    def on_closing(self):
        self.is_closing = True
        try:
            self.player.stop()
        except Exception:
            pass
        self.relock_links()
        self.save_all()
        for pool in (self.logo_pool, self.val_pool):
            if pool:
                pool.shutdown(wait=False, cancel_futures=True)
        self.root.destroy()


def main():
    if tk is None:
        print("tkinter is not installed. On Windows/macOS reinstall Python from python.org; "
              "on Linux: sudo apt install python3-tk")
        return 1
    if vlc is None:
        print("python-vlc is missing: install the required package and VLC Media Player")
        return 1
    try:  # sharp text on HiDPI Windows screens
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    root.configure(bg="#0d0d0d")
    try:
        root.iconbitmap(default="icon.ico")
    except Exception:
        pass
    app = IPTVPro(root)
    if getattr(app, "ok", False):
        root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
