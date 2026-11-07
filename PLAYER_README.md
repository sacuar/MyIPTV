# BANG IPTV Pro — New Windows player source

This folder introduces a **real desktop IPTV player**. The source is independent of the previously published BANG_IPTV_Pro.exe because that executable's original application source is not present in this repository. The existing release stays available and unchanged.

## Included features

- Embedded VLC playback of live HTTP/HLS, RTSP and RTMP streams
- Curated public free-to-access M3U presets for Bangladesh, UK, Germany, world TV, news, music, sports and movies (iptv-org)
- Load your own M3U/M3U8 from local files or HTTP(S) URLs
- Background loading, channel search, category filtering, removal of duplicate stream URLs
- Favourite channels stored on your PC, not uploaded to GitHub
- Volume, play/pause, stop, fullscreen, and shortcuts
- Playlist size cap, invalid URL handling, and UTF-8/Bengali text support

**Not yet implemented in the new player:** full XMLTV EPG, password-restricted URL viewing, five-minute auto-validation, and built-in channel logos. These existed as claims for the older release but cannot be transplanted without its source.

## Run the source on Windows

1. Install Python 3.12 or newer (and ensure Tkinter is installed).
2. Install the official [VLC Media Player](https://www.videolan.org/vlc/).
3. From the repository directory:

```powershell
python -m pip install -r requirements-player.txt
python bang_iptv_player.py
```

Select a free playlist (Bangladesh is the default), click **Load channels**, then double-click a channel. F11 makes the player fullscreen; Escape exits fullscreen, Ctrl+F searches, Ctrl+O opens a local playlist, Space toggles play/pause, and M toggles mute.

## Windows EXE build

The workflow at `.github/workflows/build-player-windows.yml` runs unit tests and packages the new application with PyInstaller. On a successful run, the **BANG-IPTV-Pro-Windows** GitHub Actions artifact contains `BANG_IPTV_Pro.exe`. This is a **new build**, not a replacement of the older GitHub Release until you test it and choose to publish it.

The EXE still needs VLC Media Player installed on the Windows computer; VLC libraries are not bundled.

## Stream availability

Public IPTV URLs are dynamic and may be geo-restricted, removed, require authorisation, or use DRM. The player removes duplicates but does **not** falsely label URLs working without checking their media. A loaded channel is not guaranteed to play.

Use only content you are authorised to access.

## Tests

```powershell
python -m unittest discover -s tests -p "test_player_core.py" -v
```

## Source and licence

This source is proposed for review. The existing repository's Unlicense and older proprietary README terms conflict; clarify the intended licensing before publicly distributing new builds.
