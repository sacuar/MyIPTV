# BANG IPTV

<p align="center">
  <img src="assets/iptv_icon.png" width="132" alt="BANG IPTV approved dark-emerald television app icon">
</p>

**Free Windows live-TV player** with M3U playlists, VLC playback, favourites and automatic playlist maintenance.

**Created and maintained by [sacuar](https://github.com/sacuar).** Built with personal time and effort. If BANG IPTV helps you, please credit the original project when sharing it.

[![Buy Me a Coffee — support the creator](https://img.shields.io/badge/Buy_Me_a_Coffee-Support_the_creator-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/sacuar)

[**Downloads**](#download) · [**Screenshots**](#screenshot) · [**Support & recognition**](#support-the-creator) · [**Code use**](#code-use-and-credits)
## Screenshot

**[Edit or replace the screenshots — simple GitHub instructions](docs/SCREENSHOTS.md)**

The current BANG IPTV application icon is [stored in this repository](screenshots/scr1.png))


*Original August 2026 Windows application. This is a genuine historical screenshot, not a verified screenshot of the v4 beta.*

<details>
<summary>View another original channel-list screenshot</summary>

![BANG IPTV — original Bangladesh channel list](![BANG IPTV v4 player](screenshots/scrr1.png))

</details>
## Download

| Version | Download | Status |
|---|---|---|
| **BANG IPTV v4.1 Beta 3** | **[Download emerald-icon EXE](https://github.com/sacuar/MyIPTV/releases/download/v4.1.0-beta.3/BANG_IPTV_v4_1_emerald.exe)** | Latest beta; approved icon in EXE and app |
| BANG IPTV v4.1 Beta 2 | [Previous stability build](https://github.com/sacuar/MyIPTV/releases/download/v4.1.0-beta.2/BANG_IPTV_v4_1_stability.exe) | Previous beta, preserved |
| BANG IPTV v4.1 Beta 1 | [Earlier v4.1 EXE](https://github.com/sacuar/MyIPTV/releases/download/v4.1.0-beta.1/BANG_IPTV_v4_1.exe) | Previous beta, preserved |
| BANG IPTV v4.0 Beta 1 | [Earlier v4 EXE](https://github.com/sacuar/MyIPTV/releases/download/v4.0.0-beta.1/BANG_IPTV_v4.exe) | Previous beta, preserved |
| **Original BANG IPTV** | [Download original stable version (31 MB)](https://github.com/sacuar/MyIPTV/releases/download/BANG_IPTV_Player_PRO/BANG_IPTV_Pro.exe) | August 2026 release; preserved unchanged |

The latest v4.1 beta is a separate application build. It does **not** replace the original stable release or previous betas. [View all releases](https://github.com/sacuar/MyIPTV/releases).

## Features

- **Distinct emerald identity:** The approved dark-green icon appears in the Windows executable, application window and app header.
- **Live TV:** Embedded VLC player, volume, mute, fullscreen and channel switching.
- **Easy browsing:** Scrollable channel list, logos, search, categories, sorting, favourites and viewing history.
- **Ready on launch:** Automatically loads your previously selected playlist. New installations default to a free Bangladesh playlist.
- **Playlist maintenance:** Automatically refresh sources, discover newly added channels, check link availability and hide confirmed broken streams.
- **Reliability:** Bounded background checks, a VLC reconnect attempt and automatic searches for matching public replacement streams.
- **Playback preference:** Balanced, High quality and Data saver; successful playback history takes priority over advertised quality labels.
- **Local files:** Open an M3U/M3U8 from disk once and v4.1 remembers it for the next launch.
- **Safer updates:** An incomplete multi-source refresh keeps the existing channel list rather than dropping sources that temporarily failed.
- **Link privacy:** Stream URLs are hidden unless you unlock their display; they are automatically hidden again after five minutes.

Broken-link detection and alternative stream searches are best-effort. A playlist can load successfully even when individual broadcasts are inaccessible, geographically restricted or no longer available.

## Getting started

1. Install [VLC Media Player](https://www.videolan.org/vlc/) for Windows.
2. Download [BANG IPTV v4.1 Beta 3](https://github.com/sacuar/MyIPTV/releases/download/v4.1.0-beta.3/BANG_IPTV_v4_1_emerald.exe), or choose an older release above.
3. Open the EXE. In v4, the saved playlist loads automatically.
4. Select a channel and double-click to watch. Use **Refresh** to update the source playlist and **Hide dead** to filter unavailable links. Use **Open file** to load your local `all.m3u8` or another M3U playlist.

Python is **not** required to run the EXE. The current beta is built and verified through GitHub's Windows build checks and automated tests. Real stream playback and replacement quality still need validation on your own computer; no source can guarantee every URL will remain available.



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

The latest application source is [`bang_iptv_v4.py`](bang_iptv_v4.py), with [stream reliability logic](stream_reliability.py), [dependencies](requirements-v4.txt), [regression tests](tests/test_v4_reliability_integration.py), the [icon artwork](assets/iptv_icon.png), [icon builder](scripts/build_iptv_icon.py), and the [current Windows release workflow](.github/workflows/publish-emerald-icon.yml).

To run v4 from source on Windows with Python 3.12+ and VLC installed:

```powershell
python -m pip install -r requirements-v4.txt
python bang_iptv_v4.py
```

The earlier [v3 source](bang_iptv_player.py) remains available. The full source used for the original August 2026 EXE is not present in this repository.

## Support the creator

BANG IPTV is **free to download and use**. Support is optional, not a fee for watching TV. Sharing feedback, reporting bugs and acknowledging the project also helps.

| ☕ Buy Me a Coffee | 💳 Stripe |
|:--|:--|
| [☕ Support via Buy Me a Coffee](https://buymeacoffee.com/sacuar) | [![Stripe support page — activation required](https://img.shields.io/badge/Stripe-Buy_Button_prepared-635BFF?logo=stripe&logoColor=white)](docs/STRIPE-SUPPORT.md) |
| Active external support option | The embedded button is ready in [the support-page source](docs/support/index.html); [GitHub Pages must first be enabled](docs/STRIPE-SUPPORT.md) for checkout to work |

**[Report a problem or suggest an improvement](https://github.com/sacuar/MyIPTV/issues)** · [**Credit the creator**](AUTHORS.md)

## Code use and credits

**BANG IPTV was started and maintained by [sacuar](https://github.com/sacuar).** If you redistribute, feature or build on the project, please give visible credit, for example **"Based on BANG IPTV by sacuar"**, with a link to [this repository](https://github.com/sacuar/MyIPTV).

- **Using official app builds:** free for personal, noncommercial use under their release-specific terms.
- **Reusing newly authored original code:** obtain permission under the [current rights notice](LICENSE); attribution is expected, and commercial repackaging may involve a paid licence.
- **Historical source code:** the repository previously used [The Unlicense](LICENSE-LEGACY-UNLICENSE.txt). Its earlier permissions cannot be withdrawn retroactively. Attribution for material covered by it is **requested as a courtesy**, not falsely presented as a legal requirement.
- **Third-party content:** broadcasts, playlists, images and dependencies retain their respective rights; they are not owned by this project.

Please preserve the author's recognition when sharing BANG IPTV. This project is free to use, and contributions or financial support are appreciated but not mandatory.
