# BANG IPTV

A Windows IPTV player for M3U playlists, with VLC playback, channel browsing, favourites and playlist management.

## Download

| Version | Download | Status |
|---|---|---|
| **BANG IPTV v4.1 Beta 1** | **[Download updated Windows EXE (23 MB)](https://github.com/sacuar/MyIPTV/releases/download/v4.1.0-beta.1/BANG_IPTV_v4_1.exe)** | Current beta; playback and reliability improvements |
| BANG IPTV v4.0 Beta 1 | [Earlier v4 EXE](https://github.com/sacuar/MyIPTV/releases/download/v4.0.0-beta.1/BANG_IPTV_v4.exe) | Previous beta, preserved |
| **Original BANG IPTV** | [Download original stable version (31 MB)](https://github.com/sacuar/MyIPTV/releases/download/BANG_IPTV_Player_PRO/BANG_IPTV_Pro.exe) | August 2026 release; preserved unchanged |

The v4.1 beta is a separate application build. It does **not** replace the original stable release or previous betas. [View all releases](https://github.com/sacuar/MyIPTV/releases).

## Features

- **Live TV:** Embedded VLC player, volume, mute, fullscreen and channel switching.
- **Easy browsing:** Scrollable channel list, logos, search, categories, sorting, favourites and viewing history.
- **Ready on launch:** Automatically loads your previously selected playlist. New installations default to a free Bangladesh playlist.
- **Playlist maintenance:** Automatically refresh sources, discover newly added channels, check link availability and hide confirmed broken streams.
- **Reliability:** Bounded background checks, a VLC reconnect attempt and automatic searches for matching public replacement streams.
- **Playback preference:** Balanced, High quality and Data saver; successful playback history takes priority over advertised quality labels.
- **Local files:** Open an M3U/M3U8 from disk once and v4.1 remembers it for the next launch.
- **Link privacy:** Stream URLs are hidden unless you unlock their display; they are automatically hidden again after five minutes.

Broken-link detection and alternative stream searches are best-effort. A playlist can load successfully even when individual broadcasts are inaccessible, geographically restricted or no longer available.

## Getting started

1. Install [VLC Media Player](https://www.videolan.org/vlc/) for Windows.
2. Download [BANG IPTV v4.1 Beta 1](https://github.com/sacuar/MyIPTV/releases/download/v4.1.0-beta.1/BANG_IPTV_v4_1.exe), or choose an older release above.
3. Open the EXE. In v4, the saved playlist loads automatically.
4. Select a channel and double-click to watch. Use **Refresh** to update the source playlist and **Hide dead** to filter unavailable links. Use **Open file** to load your local `all.m3u8` or another M3U playlist.

Python is **not** required to run the EXE. v4.1 has passed Windows build checks and automated tests. Real stream playback and replacement quality still need validation on your own computer; no source can guarantee every URL will remain available.

## Screenshots

<details>
<summary>Show screenshots of the original application</summary>

![Original BANG IPTV player](https://github.com/user-attachments/assets/c384d4f4-f754-4d7c-959c-f5482bde6049)

![Original Bangladesh channel view](https://github.com/user-attachments/assets/1205d635-c3d6-40ec-88c3-820a7ec451a4)

*These images show the original release, not the v4 beta.*

</details>

## More downloads and playlists

<details>
<summary>Earlier v3 versions and original M3U files</summary>

**Previous beta builds** — kept for comparison and rollback:

| Release | Windows download |
|---|---|
| [v3 Beta 3](https://github.com/sacuar/MyIPTV/releases/tag/v3.0.0-beta.3) | [BANG_IPTV.exe](https://github.com/sacuar/MyIPTV/releases/download/v3.0.0-beta.3/BANG_IPTV.exe) |
| [v3 Beta 2](https://github.com/sacuar/MyIPTV/releases/tag/v3.0.0-beta.2) | [BANG_IPTV_Pro.exe](https://github.com/sacuar/MyIPTV/releases/download/v3.0.0-beta.2/BANG_IPTV_Pro.exe) |
| [v3 Beta 1](https://github.com/sacuar/MyIPTV/releases/tag/v3.0.0-beta.1) | [BANG_IPTV_Pro.exe](https://github.com/sacuar/MyIPTV/releases/download/v3.0.0-beta.1/BANG_IPTV_Pro.exe) |

**Original playlist files** — preserved as references:

[Bangladesh / play.m3u](play.m3u) · [Play1.m3u](Play1.m3u) · [Germany / deu.m3u](deu.m3u) · [Radio / radio.m3u](radio.m3u) · [Movies / movies.m3u](movies.m3u)

[Original August 2026 release and settings file](https://github.com/sacuar/MyIPTV/releases/tag/BANG_IPTV_Player_PRO)

These old M3U files may contain expired or inaccessible streams. They are not verified current channel lists.

</details>

For updated public free-to-access channels, see [iptv-org](https://github.com/iptv-org/iptv), including its [Bangladesh playlist](https://iptv-org.github.io/iptv/countries/bd.m3u) and [global playlist](https://iptv-org.github.io/iptv/index.m3u). Only watch streams you are authorised to access.

## Developers

The latest application source is [`bang_iptv_v4.py`](bang_iptv_v4.py), with [stream reliability logic](stream_reliability.py), [dependencies](requirements-v4.txt), [regression tests](tests/test_v4_reliability_integration.py), and the [v4.1 Windows release workflow](.github/workflows/publish-v4-1-beta.yml).

To run v4 from source on Windows with Python 3.12+ and VLC installed:

```powershell
python -m pip install -r requirements-v4.txt
python bang_iptv_v4.py
```

The earlier [v3 source](bang_iptv_player.py) remains available. The full source used for the original August 2026 EXE is not present in this repository.

## Support

Found a bug or have an idea? [Open a GitHub issue](https://github.com/sacuar/MyIPTV/issues).

If you would like to support ongoing development, [Buy Me a Coffee](https://www.buymeacoffee.com/sacuar) is optional. Testing, feedback and code contributions are also appreciated.

**Note:** The repository's [licence](LICENSE) is the Unlicense, while earlier documentation described the original executable as proprietary. The maintainer should clarify which terms apply to each release. The link-visibility code is a convenience privacy control, not encryption.
