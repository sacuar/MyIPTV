<div align="center">

# 📺 BANG IPTV Pro

**Live TV for Windows · Free-to-access M3U playlists · VLC-powered playback**

[![Stable](https://img.shields.io/badge/Stable-August_2026-236c44)](https://github.com/sacuar/MyIPTV/releases/tag/BANG_IPTV_Player_PRO)
[![Beta](https://img.shields.io/badge/Beta-v3.0.0--beta.2-blue)](https://github.com/sacuar/MyIPTV/releases/tag/v3.0.0-beta.2)
[![Windows](https://img.shields.io/badge/Platform-Windows_10%2F11-0078D4)](https://github.com/sacuar/MyIPTV/releases)
[![Issues](https://img.shields.io/github/issues/sacuar/MyIPTV)](https://github.com/sacuar/MyIPTV/issues)

**[Download stable EXE](https://github.com/sacuar/MyIPTV/releases/download/BANG_IPTV_Player_PRO/BANG_IPTV_Pro.exe)** · **[Download new beta EXE](https://github.com/sacuar/MyIPTV/releases/download/v3.0.0-beta.2/BANG_IPTV_Pro.exe)** · **[All releases](https://github.com/sacuar/MyIPTV/releases)** · **[Report an issue](https://github.com/sacuar/MyIPTV/issues)**

</div>

---

## 📥 Choose your version

**Both Windows releases are available. The original stable release has NOT been replaced or deleted.** These are separate applications; the beta is a new implementation, not a patch to the original executable.

| | **Original stable** | **New v3.0 Beta 2** |
|---|---|---|
| Release | [BANG_IPTV_Player_PRO](https://github.com/sacuar/MyIPTV/releases/tag/BANG_IPTV_Player_PRO) | [v3.0.0-beta.2](https://github.com/sacuar/MyIPTV/releases/tag/v3.0.0-beta.2) |
| Published | 20 August 2026 | 8 November 2026 |
| Windows EXE | **[Download original (31.2 MB)](https://github.com/sacuar/MyIPTV/releases/download/BANG_IPTV_Player_PRO/BANG_IPTV_Pro.exe)** | **[Download beta (12.7 MB)](https://github.com/sacuar/MyIPTV/releases/download/v3.0.0-beta.2/BANG_IPTV_Pro.exe)** |
| Status | Existing stable release, preserved | New build; please test before relying on it |
| Source code | Original full app source not present in this repo | [Python player source](bang_iptv_player.py) and [playback/playlist core](player_core.py) available |
| VLC Media Player | Required | Required; VLC DLLs are not bundled |

**Which should I use?** Keep the **original stable** if you need its established interface and older functionality. Try **v3 beta** if you want to test the newly developed player, favourites and simpler free-playlist workflow.

## ✨ Feature comparison

The **stable** column describes features *advertised for the original executable* in earlier project documentation, not independently retested in this update. The **beta** column reflects features implemented in the current source; successful compilation does not guarantee every stream will play.

| Capability | Original stable (advertised) | v3.0 Beta 1 (implemented) |
|---|:---:|:---:|
| Watch IPTV in an embedded video player | ✅ | ✅ |
| Free-TV playlists / Bangladesh channels | ✅ | ✅ |
| Channel search and category filtering | ✅ | ✅ |
| Play / pause, stop, volume, fullscreen | ✅ | ✅ |
| Load custom M3U URLs or local files | — | ✅ |
| Remove repeated stream URLs while loading | — | ✅ |
| Save favourite channels locally | — | ✅ |
| Background playlist loading (responsive window) | — | ✅ |
| Automatic refresh of the playlist source every 30 minutes | — | ✅ Beta 2 |
| Background health checking in bounded batches | ✅ | ✅ Beta 2 |
| Hide confirmed stopped channels and VLC playback failures | — | ✅ Beta 2 |
| Manual recheck and export verified streams | — | ✅ Beta 2 |
| Electronic programme guide (EPG) display | ✅ | ❌ Not yet |
| Channel-logo display | ✅ | ❌ Not yet |
| Automatic link health checks / timed refresh | ✅ | ❌ Not yet |
| Password-protected URL visibility | ✅ | ❌ Not yet |

A dash means **not established** for that release, rather than a claim that the feature is impossible.

## 🖥️ Screenshots

The following images show the **original stable application**, not the newly rewritten v3 beta. Updated beta screenshots will be added after its Windows interface is manually checked.

<div align="center">
  <img src="https://github.com/user-attachments/assets/c384d4f4-f754-4d7c-959c-f5482bde6049" alt="Original BANG IPTV Pro Windows player screenshot" width="780">
  <p><em>Original stable player interface</em></p>
  <img src="https://github.com/user-attachments/assets/1205d635-c3d6-40ec-88c3-820a7ec451a4" alt="Original BANG IPTV Pro Bangladesh channels" width="780">
  <p><em>Original Bangladesh channel view</em></p>
</div>

## 🚀 Install and watch

**For either EXE (Windows 10/11):**

1. Install the official [VLC Media Player](https://www.videolan.org/vlc/), matching your Windows architecture.
2. Download the **original stable** or **v3 beta** EXE from the links above.
3. Run `BANG_IPTV_Pro.exe`. No separate Python installation is needed for the EXE.
4. Select a playlist, load channels, then double-click a channel to play it.

**For v3 beta specifically:** The default preset is Bangladesh — Free TV. You can switch to World, UK, Germany, News, Sports, Music or Movies, or open your own local M3U. Searching, grouping and favourites are built into the interface. A playlist loading successfully does **not** guarantee that each stream is playable: availability depends on its provider, location, format and access rights.

### v3 beta keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+O` | Open a local playlist |
| `Ctrl+F` | Focus channel search |
| `Space` | Play / pause (when not typing) |
| `M` | Mute / unmute (when not typing) |
| `F11` | Toggle fullscreen |
| `Esc` | Exit fullscreen |

**Original stable shortcuts:** See the [original release](https://github.com/sacuar/MyIPTV/releases/tag/BANG_IPTV_Player_PRO); do not assume v3 shortcuts are identical. The original application's `Ctrl+L` password control, EPG and periodic stream checking have **not** been carried over to the beta.

## 🌍 Free IPTV sources

The beta includes preset playlists from the community-maintained [iptv-org](https://github.com/iptv-org/iptv) collection. You can also load your own lawful playlist.

| Preset | Playlist |
|---|---|
| Bangladesh | [Free Bangladesh channels](https://iptv-org.github.io/iptv/countries/bd.m3u) |
| United Kingdom | [Free UK channels](https://iptv-org.github.io/iptv/countries/uk.m3u) |
| Germany | [Free German channels](https://iptv-org.github.io/iptv/countries/de.m3u) |
| Worldwide | [Global playlist](https://iptv-org.github.io/iptv/index.m3u) |
| News | [News playlist](https://iptv-org.github.io/iptv/categories/news.m3u) |
| Sports | [Sports playlist](https://iptv-org.github.io/iptv/categories/sports.m3u) |
| Music | [Music playlist](https://iptv-org.github.io/iptv/categories/music.m3u) |
| Movies | [Movies playlist](https://iptv-org.github.io/iptv/categories/movies.m3u) |

These are free-to-access playlist indexes, **not a promise of channel uptime or rights to all content**. Stream links may expire, be geoblocked, require authorisation, or be DRM-protected. The project does not host these broadcasts.

## 🧑‍💻 Source code, tools and building

The source of the **new v3 beta** is in this repository. The full source code used to build the **original August stable EXE** is not available here.

| File | Purpose |
|---|---|
| [`bang_iptv_player.py`](bang_iptv_player.py) | New desktop player interface and VLC controls |
| [`player_core.py`](player_core.py) | M3U parsing, preset lists, channel filtering and duplicate removal |
| [`requirements-player.txt`](requirements-player.txt) | New player's Python dependency |
| [`gui2.py`](gui2.py) | Separate M3U checking, filtering and exporting utility |
| [`playlist_service.py`](playlist_service.py) | Playlist utility logic |
| [`m3u_export.py`](m3u_export.py) | Extended M3U metadata export |
| [`scripts/clean_playlists.py`](scripts/clean_playlists.py) | On-demand deduplication and optional HTTP reachability probe |
| [`tests/`](tests) | Automated checks |
| [Windows player build workflow](.github/workflows/build-player-windows.yml) | Builds an EXE artifact from source |
| [Beta release workflow](.github/workflows/publish-player-beta.yml) | Publishes a separately tagged prerelease |

### Run v3 from source

Install Python 3.12+ and VLC Media Player. From a clone of this repository:

```powershell
python -m pip install -r requirements-player.txt
python bang_iptv_player.py
```

### Run the playlist-checking utility

This is a **separate tool**, not the main video player:

```powershell
python -m pip install m3u-parser
python gui2.py
```

It supports URL/local-file loading, optional background stream checks, category/status filtering, UTF-8 M3U export and removal of duplicate URLs. Links that haven't been checked are marked *unchecked*, not working.

### Clean old playlist files

```powershell
python scripts/clean_playlists.py Play1.m3u play.m3u --output cleaned.m3u
python scripts/clean_playlists.py Play1.m3u --verify --output reachable.m3u
```

The first command deduplicates without testing streams. The second exports URLs that respond to HTTP checks; a positive HTTP response does not prove actual media playback. Original input files are not overwritten. Some legacy playlists were removed from the current repo tree during cleanup but remain accessible in Git history.

### Tests and builds

```powershell
python -m unittest discover -s tests -v
```

The [GitHub Actions page](https://github.com/sacuar/MyIPTV/actions) contains the Windows EXE build logs. Passing automated tests and building an EXE do **not** replace manual playback testing on Windows.

## 🔄 Automatic refresh and broken-channel removal (Beta 2)

The new player now has **Auto-check links**, **Auto-refresh list**, **Hide stopped**, **Check now** and **Refresh** controls in the channel sidebar.

- **Stream checks:** Small background batches of up to 48 URLs are processed with up to 8 workers. Large playlists are scanned progressively, not all at once.
- **Stopped links:** Two HTTP 404/410 responses mark a link offline; VLC playback failures also mark channels unavailable. **Hide stopped** removes these from the visible list. Uncheck it to see them again.
- **Temporary problems:** 403/401 access restrictions, network timeouts and uncertain media responses do not silently delete channels. HTTP success alone is not proof of playable video.
- **Playlist updates:** Refresh manually at any time, or leave **Auto-refresh list** enabled for a new fetch every 30 minutes while the app is running.
- **Clean playlist:** Use **Save verified working channels as M3U** to create an exported playlist containing only links that were positively checked. Your original M3U source is not overwritten.

Checks run while the application is open. Channels hidden as stopped remain recoverable and can be checked again if the stream provider restores service. Full checks of very large global playlists can take longer than five minutes.

## 📌 Release history

- **8 November 2026 — [v3.0 Beta 2](https://github.com/sacuar/MyIPTV/releases/tag/v3.0.0-beta.2):** Automatic playlist reload, background health checks, Hide stopped option, manual recheck and verified M3U export.\n- **8 November 2026 — [v3.0 Beta 1](https://github.com/sacuar/MyIPTV/releases/tag/v3.0.0-beta.1):** New Python-based Windows player with VLC playback, free-playlist presets, favourites, search, categories, duplicate removal and independent EXE build.
- **20 August 2026 — [Original stable release](https://github.com/sacuar/MyIPTV/releases/tag/BANG_IPTV_Player_PRO):** Preserved legacy Windows player; its earlier documentation described EPG, channel icons, link validation and password-restricted link visibility.

The beta does **not** replace the original release. Further versions should be tagged separately.

## 🛡️ Licence and streaming responsibility

The repository's [`LICENSE`](LICENSE) contains the Unlicense, while older project documentation described the software as proprietary. These statements conflict. The maintainer should clarify licensing for the source and separately distributed binaries; this README does not change the existing licence or revoke any previously granted rights.

Only watch streams you are entitled to access. Playlist entries are third-party links; this repository does not host the broadcast content.

## 💬 Help and support

- 🐛 **[Report a bug or request a feature](https://github.com/sacuar/MyIPTV/issues)** — mention **Original stable** or **v3 beta**, your Windows version, and the steps to reproduce.
- 📦 **[All downloads and releases](https://github.com/sacuar/MyIPTV/releases)**
- 💻 **[Project source](https://github.com/sacuar/MyIPTV)**
- ☕ **[Support development](https://www.buymeacoffee.com/sacuar)**

<div align="center">
  <strong>BANG IPTV Pro</strong><br>
  Windows IPTV playback · Free playlist tools · Maintained by <a href="https://github.com/sacuar">sacuar</a>
</div>
