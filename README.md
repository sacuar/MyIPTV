# BANG IPTV

A Windows IPTV player for M3U playlists, with VLC playback, channel browsing, favourites and playlist management.

## Download

| Version | Download | Status |
|---|---|---|
| **BANG IPTV v4.0 Beta 1** | [Download for Windows (23 MB)](https://github.com/sacuar/MyIPTV/releases/download/v4.0.0-beta.1/BANG_IPTV_v4.exe) | New interface; still being tested |
| **Original BANG IPTV** | [Download original stable version (31 MB)](https://github.com/sacuar/MyIPTV/releases/download/BANG_IPTV_Player_PRO/BANG_IPTV_Pro.exe) | August 2026 release; preserved unchanged |

The v4 beta is a separate application build. It does **not** replace the original stable release. [View all releases](https://github.com/sacuar/MyIPTV/releases).

## Features

- **Live TV:** Embedded VLC player, volume, mute, fullscreen and channel switching.
- **Easy browsing:** Scrollable channel list, logos, search, categories, sorting, favourites and viewing history.
- **Ready on launch:** Automatically loads your previously selected playlist. New installations default to a free Bangladesh playlist.
- **Playlist maintenance:** Refresh sources, check channel availability and hide confirmed broken streams.
- **Link privacy:** Stream URLs are hidden unless you unlock their display; they are automatically hidden again after five minutes.

Broken-link detection and alternative stream searches are best-effort. A playlist can load successfully even when individual broadcasts are inaccessible, geographically restricted or no longer available.

## Getting started

1. Install [VLC Media Player](https://www.videolan.org/vlc/) for Windows.
2. Download the [latest v4 beta](https://github.com/sacuar/MyIPTV/releases/download/v4.0.0-beta.1/BANG_IPTV_v4.exe), or use the original stable version above.
3. Open the EXE. In v4, the saved playlist loads automatically.
4. Select a channel and double-click to watch. Use **Update now** to refresh your playlist, and **Hide dead** to filter out known unavailable links.

Python is **not** required to run the EXE. v4 has passed Windows build checks and automated tests, but playback with actual streams still needs validation on individual computers.

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

The latest application source is [`bang_iptv_v4.py`](bang_iptv_v4.py). The [requirements](requirements-v4.txt), [regression tests](tests/test_v4_regression.py) and [Windows build workflow](.github/workflows/publish-v4-beta.yml) are also available.

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
