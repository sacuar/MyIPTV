<div align="center">

# 📺 BANG IPTV

**Windows live TV player · M3U playlists · VLC playback**

[![Stable](https://img.shields.io/badge/Stable-August_2026-green)](https://github.com/sacuar/MyIPTV/releases/tag/BANG_IPTV_Player_PRO)
[![Latest beta](https://img.shields.io/badge/Latest_beta-v4.0.0--beta.1-blue)](https://github.com/sacuar/MyIPTV/releases/tag/v4.0.0-beta.1)
[![Windows](https://img.shields.io/badge/Windows-10%20%2F%2011-0078D4)](https://github.com/sacuar/MyIPTV/releases)

**[Download v4 beta EXE](https://github.com/sacuar/MyIPTV/releases/download/v4.0.0-beta.1/BANG_IPTV_v4.exe)** · **[Download old stable EXE](https://github.com/sacuar/MyIPTV/releases/download/BANG_IPTV_Player_PRO/BANG_IPTV_Pro.exe)** · **[All versions](https://github.com/sacuar/MyIPTV/releases)** · **[Report a problem](https://github.com/sacuar/MyIPTV/issues)**

</div>

---

## 📥 Downloads — all versions in one place

The **original August 2026 stable release and all v3 beta versions remain available and unchanged**. The v4 app is a separate build; it does not replace your existing executable.

| Version | Published | Windows EXE | Notes |
|---|---|---|---|
| **v4 Beta 1 — current beta** | 8 Nov 2026 | **[BANG_IPTV_v4.exe (23 MB)](https://github.com/sacuar/MyIPTV/releases/download/v4.0.0-beta.1/BANG_IPTV_v4.exe)** | Richer v4 interface, channel list scrollbar, startup loading, logos, sorting, auto refresh and broken-link filtering |
| v3 Beta 3 | 8 Nov 2026 | [BANG_IPTV.exe](https://github.com/sacuar/MyIPTV/releases/download/v3.0.0-beta.3/BANG_IPTV.exe) | Simpler interface, private link display, public alternative search |
| v3 Beta 2 | 8 Nov 2026 | [BANG_IPTV_Pro.exe](https://github.com/sacuar/MyIPTV/releases/download/v3.0.0-beta.2/BANG_IPTV_Pro.exe) | Stream health checks and auto-refresh |
| v3 Beta 1 | 8 Nov 2026 | [BANG_IPTV_Pro.exe](https://github.com/sacuar/MyIPTV/releases/download/v3.0.0-beta.1/BANG_IPTV_Pro.exe) | First rewritten Windows player |
| **Original stable** | 20 Aug 2026 | **[BANG_IPTV_Pro.exe (31.2 MB)](https://github.com/sacuar/MyIPTV/releases/download/BANG_IPTV_Player_PRO/BANG_IPTV_Pro.exe)** | Preserved original release and settings asset |

**Recommendation:** Keep the original stable EXE if it is your known working version. Test the new v4 beta separately; Windows compilation passed but full stream playback has not yet been confirmed on users' computers.

## 🖥️ Interface

<details>
<summary>View screenshots of the original stable version</summary>

![Original player interface](https://github.com/user-attachments/assets/c384d4f4-f754-4d7c-959c-f5482bde6049)

![Original Bangladesh channels](https://github.com/user-attachments/assets/1205d635-c3d6-40ec-88c3-820a7ec451a4)

*These are historical screenshots, not verified v4 screenshots.*

</details>

### What v4 adds or restores

- **Channel sidebar and vertical scrollbar:** Treeview channel list with mouse/scrollbar navigation; lazy loading of channel logos so large lists stay responsive.
- **Automatic playlist loading at startup:** Restores the last source on opening. Fresh installations default to the Bangladesh free-TV playlist.
- **More ways to browse:** Search, categories, status filters, sorting, favourites pinned to the top, recent history, country/language lists and merged playlists.
- **Full player controls:** VLC video area, previous/next channel, play/pause, seek, volume, mute, fullscreen and an on-screen channel name.
- **Regular playlist updates:** Reload the source automatically at a selected interval (5–120 minutes) while the program is open, or click **Update now**.
- **Broken-link handling:** New installs default to **Hide dead**. Link checks run in the background and the list is updated as dead statuses become available. **Fix dead links** searches matching alternatives from loaded playlists and remembers successful repairs.
- **Private URL display:** Links are hidden by default. `Ctrl+L` opens a masked unlock prompt; visibility automatically relocks after five minutes.

**Important:** The app hides unavailable channels in the view; it does **not delete them from a remote playlist**. HTTP 403, access restrictions and temporary connection errors are treated as inconclusive rather than proof that a broadcaster is permanently unavailable. Link repair is best-effort; working endpoints and video decoding cannot be guaranteed.

### Feature comparison

| Feature | Original stable (previously advertised) | v4 Beta 1 |
|---|---|---|
| Video playback with VLC | Yes | Yes |
| Channels, groups and search | Yes | Yes |
| Scrollable channel list | Yes | Yes — tested in Tkinter |
| Auto-load saved source on opening | Not confirmed | Yes — tested in Tkinter |
| Channel logos | Yes | Yes |
| Favourites and history | Yes | Yes |
| Playlist refresh / link validation | Yes | Yes |
| Hide known dead channels | Not confirmed | Yes |
| Replacement for stopped links | Not confirmed | Best-effort from loaded sources |
| Full EPG display | Advertised | Not implemented in v4 |
| Link visibility lock | Advertised | Yes; UI privacy only |

Descriptions of the original version come from previous project documentation and were not independently verified during this update.

## 🚀 Install and start watching

1. Install [VLC Media Player](https://www.videolan.org/vlc/) for Windows (matching the application architecture).
2. Download **[BANG_IPTV_v4.exe](https://github.com/sacuar/MyIPTV/releases/download/v4.0.0-beta.1/BANG_IPTV_v4.exe)**.
3. Open the executable. **It automatically starts loading your last playlist** (Bangladesh free TV if none was previously saved).
4. Scroll or search for a channel and double-click to play. Choose **Hide dead** to exclude links confirmed as stopped; select **Update now** to fetch the current playlist.

There is no need to install Python when running the EXE. Internet access is required for online playlists; some streams may be geo-restricted or require separate authorisation.

### Keyboard shortcuts (v4)

| Shortcut | Action |
|---|---|
| `Ctrl+F` | Focus channel search |
| `Ctrl+R` | Refresh selected playlist |
| `Ctrl+L` | Reveal or hide stream links via private prompt |
| `Page Up` / `Page Down` | Previous / next channel |
| `Space` | Play / pause |
| `F` or `F11` | Fullscreen |
| `Escape` | Exit fullscreen |
| `M` | Mute |
| `↑` / `↓` | Volume |

## 🌍 Free M3U sources

v4 includes country, category and language presets and supports custom URLs and local M3U files. Examples from the community-maintained [iptv-org](https://github.com/iptv-org/iptv) index:

| List | Link |
|---|---|
| Bangladesh | [Bangladesh M3U](https://iptv-org.github.io/iptv/countries/bd.m3u) |
| UK | [United Kingdom M3U](https://iptv-org.github.io/iptv/countries/gb.m3u) |
| Global | [World M3U](https://iptv-org.github.io/iptv/index.m3u) |
| News | [News M3U](https://iptv-org.github.io/iptv/categories/news.m3u) |
| Sports | [Sports M3U](https://iptv-org.github.io/iptv/categories/sports.m3u) |
| Music | [Music M3U](https://iptv-org.github.io/iptv/categories/music.m3u) |

These are third-party playlist indexes, not a guarantee that every channel plays. Only use streams you are authorised to access.

## 🧑‍💻 Source code, checks and builds

The source of the original August 2026 EXE is not present in this repository. The v4 source and earlier v3 source **are** available, with historical releases retained.

| File | Purpose |
|---|---|
| [`bang_iptv_v4.py`](bang_iptv_v4.py) | **Latest v4 player** — UI, playback, sorting, logos, refresh and link repair |
| [`requirements-v4.txt`](requirements-v4.txt) | Required Python packages for v4 |
| [`tests/test_v4_regression.py`](tests/test_v4_regression.py) | Offline v4 regression tests |
| [v4 Windows build workflow](.github/workflows/publish-v4-beta.yml) | Test, package and publish the separate v4 beta |
| [`bang_iptv_player.py`](bang_iptv_player.py) | Earlier v3 player for comparison and rollback |
| [`player_core.py`](player_core.py) | v3 channel parsing and filtering |
| [`gui2.py`](gui2.py) | Separate playlist validation/export tool |
| [`scripts/clean_playlists.py`](scripts/clean_playlists.py) | Deduplicate or probe local M3U sources |
| [`tests/`](tests) | Automated checks for the project |

To run v4 from source on Windows, install Python 3.12+ and VLC Media Player:

```powershell
python -m pip install -r requirements-v4.txt
python bang_iptv_v4.py
```

To run the v4 regression suite:

```powershell
python -m unittest discover -s tests -p "test_v4_regression.py" -v
```

For the older v3 source, use `requirements-player.txt` and `bang_iptv_player.py`. The independent `gui2.py` M3U utility also needs `m3u-parser`.

**Validation scope:** The v4 code passed a local Tkinter UI smoke test using a mocked VLC backend, including scrollbar visibility, usable scrolling with 100 channels, and startup loading. GitHub Actions passed Windows compilation and automated tests and published a 23 MB EXE. Live decoding of real streams on your Windows machine still requires manual testing.

## 🛡️ Licensing, privacy and support

The `LICENSE` file currently contains the Unlicense, while earlier documentation described the old application as proprietary. The maintainer should clarify which terms apply to the old binary and new source. Updating this README does not change the licence or revoke previously granted rights.

The stream-link unlock is **visual privacy only**, not strong security or encryption. Do not commit passwords, private M3U credentials or access tokens to GitHub, and redact them in bug reports.

- [Report a bug or request an improvement](https://github.com/sacuar/MyIPTV/issues)
- [See all GitHub releases](https://github.com/sacuar/MyIPTV/releases)
- [GitHub Actions build history](https://github.com/sacuar/MyIPTV/actions)
- [Optional project support](https://www.buymeacoffee.com/sacuar)

<div align="center">
<strong>BANG IPTV</strong> · Windows IPTV player · <a href="https://github.com/sacuar">sacuar</a>
</div>
