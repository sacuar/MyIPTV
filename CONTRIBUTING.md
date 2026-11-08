# Contributing to BANG IPTV Pro

Thank you for helping improve the BANG IPTV Pro Windows player. Contributions of **bug reports, test results, translations, accessibility improvements, code fixes and documentation** are welcome.

## Ways to contribute

- **Report a bug:** [Open an issue](https://github.com/sacuar/MyIPTV/issues/new/choose). Include the player version, Windows version, steps to reproduce, expected result and actual result.
- **Suggest an enhancement:** Use the GitHub [Feature Request](https://github.com/sacuar/MyIPTV/issues/new?template=feature-request.md) template.
- **Test the beta:** Check playlist loading, VLC playback, favourites, reconnection and health-check behaviour. Mention whether you used the original stable release or the latest beta.
- **Contribute code:** Open an issue first for larger changes; then create a branch, add focused tests, and open a pull request against `main`.
- **Translate or improve documentation:** UI wording, instructions, and translations are useful, especially for Bengali and English.
- **Support development (optional):** [Buy Me a Coffee](https://www.buymeacoffee.com/sacuar). No donation is needed to report problems or contribute code.

## Local development

Install Python 3.12+ and VLC Media Player on Windows, then from the repository root:

```powershell
python -m pip install -r requirements-player.txt
python -m unittest discover -s tests -v
python bang_iptv_player.py
```

Tests for playlist parsing, validation and channel navigation should avoid relying on live third-party streams. For code changes, keep playback, UI and tests consistent and describe what you tested.

## Pull request checklist

- The patch fixes a specific problem or adds a clearly described feature.
- Existing stable GitHub releases remain available; don't overwrite historic tags or EXE files.
- New code avoids blocking Tkinter's UI thread with network requests.
- Tests pass: `python -m unittest discover -s tests -v`.
- Playlist links and logs contain no passwords, access tokens, user credentials, private identifiers or copyrighted media.
- New functionality is clearly distinguished from what has been tested on real Windows devices.

## Security and licensing

Do **not** publish credentials, authenticated M3U URLs, private headers, sensitive screenshots or secret configuration in issues or pull requests. Replace sensitive URL tokens with `[REDACTED]`. Use only streams that you are entitled to access.

**Licensing requires maintainer clarification:** The repository contains an Unlicense `LICENSE` file, while previous documentation described the original executable as proprietary. Please review the [licensing note in README](README.md) before making substantial code submissions. This document does not change the repository licence or claim that all original binary assets share it.

## Review and releases

Pull requests are reviewed against `main`. Automated Windows build jobs may create test EXE artifacts, but contributors should not overwrite or delete the original stable release. Tested changes can be published under a **new prerelease tag** after approval.

Thanks for contributing to a faster, more reliable, easier-to-use BANG IPTV Pro.
