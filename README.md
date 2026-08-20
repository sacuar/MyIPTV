# 🎬 BANG IPTV Pro

<div align="center">
    ##<img src="https://raw.githubusercontent.com/sacuar/MyIPTV/main/photo/rebrand.ly.18b0e6.png" alt="BANG IPTV Pro" width="200">
    <br>
    <strong>Professional IPTV Player with Auto-Validation</strong>
    <br>
    <strong>Bangladesh Category · EPG Support · Music Channels</strong>
</div>

---

## 📢 Announcement

### 🚀 BANG IPTV Pro v2.0 - Happy New Release!

I'm excited to announce the release of **BANG IPTV Pro v2.0** - a professional IPTV player with automatic link validation, Bangladesh category support, channel icons, and EPG integration.

**New Features:**
- ✅ Automatic link validation (checks working/dead links)
- ✅ Bangladesh channels category
- ✅ Channel icons from online databases
- ✅ EPG (Electronic Program Guide) support
- ✅ Password-protected link visibility
- ✅ Background auto-update every 5 minutes
- ✅ 650+ Music channels
- ✅ Professional dark theme UI

---

## 📺 Features

| Feature | Status | Description |
|---------|--------|-------------|
| 🔗 Auto Link Validation | ✅ | Automatically checks and marks working/dead links |
| 🇧🇩 Bangladesh Category | ✅ | Dedicated BD channels from multiple sources |
| 🖼️ Channel Icons | ✅ | Fetches icons from online databases |
| 📅 EPG Support | ✅ | Electronic Program Guide integration |
| 🔒 Password Protection | ✅ | Default password: `simple` - Ctrl+L to reveal links |
| 🔄 Auto-Update | ✅ | Background link validation every 5 minutes |
| 📺 Professional UI | ✅ | Dark theme, right-click menu, status indicators |
| 🎵 Music Channels | ✅ | 650+ music channels from iptv-org |
| 🎬 Movie Channels | ✅ | Dedicated movie category |
| ⚽ Sports Channels | ✅ | Sports channels worldwide |
| 📰 News Channels | ✅ | News channels worldwide |

---

## 📦 Sources Included

| Source | Description | Channels |
|--------|-------------|----------|
| 🌍 World IPTV | Free-TV IPTV collection | 5,000+ |
| 📺 Global TV | iptv-org official playlist | 10,000+ |
| 🇧🇩 Bangladesh IPTV | Bangladeshi channels | 200+ |
| 🇧🇩 BDIX IPTV | BDIX supported channels | 600+ |
| 🇧🇩 Bangladesh (iptv-org) | Official BD channels | 100+ |
| 🇬🇧 UK Free | UK free channels | 500+ |
| 🇺🇸 US Free | US free channels | 500+ |
| 📰 News | News worldwide | 1,000+ |
| ⚽ Sports | Sports channels | 500+ |
| 🎵 Music | Music channels | 650+ |
| 🎬 Movies | Movie channels | 300+ |

---

## 🎵 Music Channels

Access music channels by:
1. Loading the **"🌍 World IPTV"** or **"📺 Global TV"** source
2. Selecting **"Music"** from the category filter

**Direct Music Playlist:**
```
https://iptv-org.github.io/iptv/categories/music.m3u
```

---

## 📸 Screenshots

### Main Interface
<p align="center">
    <img src="screenshots/scr1.jpg" width="800" alt="Main Interface">
</p>

### Bangladesh Channels
<p align="center">
    <img src="screenshots/scr2.jpg" width="800" alt="Bangladesh Channels">
</p>

### Music Channels
<p align="center">
    <img src="screenshots/scr3.jpg" width="800" alt="Music Channels">
</p>

---

## 🔧 Installation

### Method 1: Run from Source

#### Requirements
- Python 3.10 or higher
- VLC Media Player installed

#### Install Dependencies
```bash
pip install python-vlc Pillow requests
```

#### Run the App
```bash
python iptv_pro.py
```

### Method 2: Download EXE

Download the latest release from:
**[Releases Page](https://github.com/sacuar/BANG-IPTV-Pro/releases/latest)**

No Python installation required!

---

## 🚀 How to Use

1. **Launch the app** (double-click `BANG_IPTV_Pro.exe` or run `python iptv_pro.py`)
2. **Select a source** from the dropdown menu
3. Click **"📥 Load"** to load channels
4. **Browse channels** - scroll through the list
5. **Search** - type to filter channels by name
6. **Filter by category** - use the category dropdown
7. **Double-click** a channel to watch
8. **Controls**: Play/Pause, Stop, Previous/Next channel

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `←` `→` | Seek backward/forward 5s |
| `↑` `↓` | Volume up/down |
| `M` | Mute |
| `F` | Fullscreen |
| `Esc` | Exit fullscreen |
| `Ctrl+L` | Toggle link visibility (password: `simple`) |
| `Ctrl+R` | Refresh playlist |

---

## 🔗 Working M3U Links

### Main Playlists

| Type | URL |
|------|-----|
| **Main Playlist** | `https://raw.githubusercontent.com/sacuar/MyIPTV/main/play.m3u` |
| **Movies** | `https://raw.githubusercontent.com/sacuar/MyIPTV/main/movies.m3u` |
| **Radio** | `https://raw.githubusercontent.com/sacuar/MyIPTV/main/radio.m3u` |
| **Music/Bangla/Hindi** | Short: `https://cutt.ly/gRXVGjq` |

### German Playlists

```
https://raw.githubusercontent.com/sacuar/MyIPTV/main/deu.m3u
https://raw.githubusercontent.com/sacuar/MyIPTV/main/deplay.m3u
```

### Bangladesh Channels

```
https://raw.githubusercontent.com/sacuar/MyIPTV/main/play.m3u
```

---

## 🛠️ Build EXE

### Batch Builder
Run the included batch file:
```batch
build_exe.bat
```

### Manual PyInstaller
```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "BANG_IPTV_Pro" iptv_pro.py
```

---

## 📋 Requirements

### For Source Code
- Windows 10/11, Linux, or macOS
- Python 3.10+
- VLC Media Player installed
- pip (Python package manager)

### For EXE Version
- Windows 10/11
- VLC Media Player installed
- No Python required

---

## 🔐 Password Protection

Default password: **`simple`**

- Press `Ctrl+L` to toggle link visibility
- Enter the password to reveal channel URLs
- Links are hidden by default for normal users

---

## 📊 IPTV Stream Checker

Checks working and not working links in an M3U file. Open the M3U file and press check. You can also modify the red invalid links and update the M3U.

**Download:** [IPTV Stream Checker](https://github.com/sacuar/IPTV_stream_checker/releases/tag/IPTV-M3U-CHECK)

---

## 🌟 Support the Project

If you find this software useful, you can support its development:

<!--START_SECTION:buy-me-a-coffee-->
<a href="https://www.buymeacoffee.com/sacuar" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174">
</a>
<!--END_SECTION:buy-me-a-coffee-->

---

## ⚠️ Legal & Copyright

**© 2024 BANG IPTV Pro - All Rights Reserved**

This software is **proprietary** and **not for copying, distribution, or sale** without explicit permission from the author.

### ❌ Not Permitted:
- Commercial use
- Resale or redistribution
- Copying or modification without permission
- Claiming as your own work

### ✅ Permitted:
- Personal use
- Non-commercial use
- Testing and evaluation

---

## 📜 Disclaimer

All IPTV streams are sourced from publicly available playlists. Users are responsible for ensuring they have the right to access any content they stream. This software does not host or provide any copyrighted content.

---

## 📝 Changelog

### v2.0 (2024)
- ✅ Added automatic link validation
- ✅ Added Bangladesh category with multiple sources
- ✅ Added channel icons from online databases
- ✅ Added EPG support
- ✅ Added password-protected link visibility (default: `simple`)
- ✅ Added background auto-update every 5 minutes
- ✅ Added 650+ music channels
- ✅ Added professional dark theme UI
- ✅ Added right-click menu for channels
- ✅ Added copy URL functionality (password protected)
- ✅ Improved performance and stability

### v1.0 (2023)
- ✅ Initial release
- ✅ Basic IPTV player functionality
- ✅ Multiple source support
- ✅ Category filtering
- ✅ Search functionality

---

## 📞 Contact & Support

- **GitHub:** [sacuar](https://github.com/sacuar)
- **Buy Me a Coffee:** [buymeacoffee.com/sacuar](https://buymeacoffee.com/sacuar)
- **Issues:** [Report a Bug](https://github.com/sacuar/BANG-IPTV-Pro/issues)

---

## ❤️ Enjoy!

Enjoy!! :heart::heart:

---

<p align="center">
    <img src="https://raw.githubusercontent.com/sacuar/MyIPTV/main/photo/rebrand.ly.18b0e6.png" alt="QR Code" height="120">
    <br>
    <strong>BANG IPTV Pro</strong>
    <br>
    Professional IPTV Player with Auto-Validation
</p># 🎬 BANG IPTV Pro

<div align="center">
    <img src="https://raw.githubusercontent.com/sacuar/MyIPTV/main/photo/rebrand.ly.18b0e6.png" alt="BANG IPTV Pro" width="200">
    <br>
    <strong>Professional IPTV Player with Auto-Validation</strong>
    <br>
    <strong>Bangladesh Category · EPG Support · Music Channels</strong>
</div>

---

## 📢 Announcement

### 🚀 BANG IPTV Pro v2.0 - Happy New Release!

I'm excited to announce the release of **BANG IPTV Pro v2.0** - a professional IPTV player with automatic link validation, Bangladesh category support, channel icons, and EPG integration.

**New Features:**
- ✅ Automatic link validation (checks working/dead links)
- ✅ Bangladesh channels category
- ✅ Channel icons from online databases
- ✅ EPG (Electronic Program Guide) support
- ✅ Password-protected link visibility
- ✅ Background auto-update every 5 minutes
- ✅ 650+ Music channels
- ✅ Professional dark theme UI

---

## 📺 Features

| Feature | Status | Description |
|---------|--------|-------------|
| 🔗 Auto Link Validation | ✅ | Automatically checks and marks working/dead links |
| 🇧🇩 Bangladesh Category | ✅ | Dedicated BD channels from multiple sources |
| 🖼️ Channel Icons | ✅ | Fetches icons from online databases |
| 📅 EPG Support | ✅ | Electronic Program Guide integration |
| 🔒 Password Protection | ✅ | Default password: `simple` - Ctrl+L to reveal links |
| 🔄 Auto-Update | ✅ | Background link validation every 5 minutes |
| 📺 Professional UI | ✅ | Dark theme, right-click menu, status indicators |
| 🎵 Music Channels | ✅ | 650+ music channels from iptv-org |
| 🎬 Movie Channels | ✅ | Dedicated movie category |
| ⚽ Sports Channels | ✅ | Sports channels worldwide |
| 📰 News Channels | ✅ | News channels worldwide |

---

## 📦 Sources Included

| Source | Description | Channels |
|--------|-------------|----------|
| 🌍 World IPTV | Free-TV IPTV collection | 5,000+ |
| 📺 Global TV | iptv-org official playlist | 10,000+ |
| 🇧🇩 Bangladesh IPTV | Bangladeshi channels | 200+ |
| 🇧🇩 BDIX IPTV | BDIX supported channels | 600+ |
| 🇧🇩 Bangladesh (iptv-org) | Official BD channels | 100+ |
| 🇬🇧 UK Free | UK free channels | 500+ |
| 🇺🇸 US Free | US free channels | 500+ |
| 📰 News | News worldwide | 1,000+ |
| ⚽ Sports | Sports channels | 500+ |
| 🎵 Music | Music channels | 650+ |
| 🎬 Movies | Movie channels | 300+ |

---

## 🎵 Music Channels

Access music channels by:
1. Loading the **"🌍 World IPTV"** or **"📺 Global TV"** source
2. Selecting **"Music"** from the category filter

**Direct Music Playlist:**
```
https://iptv-org.github.io/iptv/categories/music.m3u
```

---

## 📸 Screenshots

### Main Interface
<p align="center">
    <img src="screenshots/scr1.jpg" width="800" alt="Main Interface">
</p>

### Bangladesh Channels
<p align="center">
    <img src="screenshots/scr2.jpg" width="800" alt="Bangladesh Channels">
</p>

### Music Channels
<p align="center">
    <img src="screenshots/scr3.jpg" width="800" alt="Music Channels">
</p>

---

## 🔧 Installation

### Method 1: Run from Source

#### Requirements
- Python 3.10 or higher
- VLC Media Player installed

#### Install Dependencies
```bash
pip install python-vlc Pillow requests
```

#### Run the App
```bash
python iptv_pro.py
```

### Method 2: Download EXE

Download the latest release from:
**[Releases Page](https://github.com/sacuar/BANG-IPTV-Pro/releases/latest)**

No Python installation required!

---

## 🚀 How to Use

1. **Launch the app** (double-click `BANG_IPTV_Pro.exe` or run `python iptv_pro.py`)
2. **Select a source** from the dropdown menu
3. Click **"📥 Load"** to load channels
4. **Browse channels** - scroll through the list
5. **Search** - type to filter channels by name
6. **Filter by category** - use the category dropdown
7. **Double-click** a channel to watch
8. **Controls**: Play/Pause, Stop, Previous/Next channel

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `←` `→` | Seek backward/forward 5s |
| `↑` `↓` | Volume up/down |
| `M` | Mute |
| `F` | Fullscreen |
| `Esc` | Exit fullscreen |
| `Ctrl+L` | Toggle link visibility (password: `simple`) |
| `Ctrl+R` | Refresh playlist |

---

## 🔗 Working M3U Links

### Main Playlists

| Type | URL |
|------|-----|
| **Main Playlist** | `https://raw.githubusercontent.com/sacuar/MyIPTV/main/play.m3u` |
| **Movies** | `https://raw.githubusercontent.com/sacuar/MyIPTV/main/movies.m3u` |
| **Radio** | `https://raw.githubusercontent.com/sacuar/MyIPTV/main/radio.m3u` |
| **Music/Bangla/Hindi** | Short: `https://cutt.ly/gRXVGjq` |

### German Playlists

```
https://raw.githubusercontent.com/sacuar/MyIPTV/main/deu.m3u
https://raw.githubusercontent.com/sacuar/MyIPTV/main/deplay.m3u
```

### Bangladesh Channels

```
https://raw.githubusercontent.com/sacuar/MyIPTV/main/play.m3u
```

---

## 🛠️ Build EXE

### Batch Builder
Run the included batch file:
```batch
build_exe.bat
```

### Manual PyInstaller
```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "BANG_IPTV_Pro" iptv_pro.py
```

---

## 📋 Requirements

### For Source Code
- Windows 10/11, Linux, or macOS
- Python 3.10+
- VLC Media Player installed
- pip (Python package manager)

### For EXE Version
- Windows 10/11
- VLC Media Player installed
- No Python required

---

## 🔐 Password Protection

Default password: **`simple`**

- Press `Ctrl+L` to toggle link visibility
- Enter the password to reveal channel URLs
- Links are hidden by default for normal users

---

## 📊 IPTV Stream Checker

Checks working and not working links in an M3U file. Open the M3U file and press check. You can also modify the red invalid links and update the M3U.

**Download:** [IPTV Stream Checker](https://github.com/sacuar/IPTV_stream_checker/releases/tag/IPTV-M3U-CHECK)

---

## 🌟 Support the Project

If you find this software useful, you can support its development:

<!--START_SECTION:buy-me-a-coffee-->
<a href="https://www.buymeacoffee.com/sacuar" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174">
</a>
<!--END_SECTION:buy-me-a-coffee-->

---

## ⚠️ Legal & Copyright

**© 2024 BANG IPTV Pro - All Rights Reserved**

This software is **proprietary** and **not for copying, distribution, or sale** without explicit permission from the author.

### ❌ Not Permitted:
- Commercial use
- Resale or redistribution
- Copying or modification without permission
- Claiming as your own work

### ✅ Permitted:
- Personal use
- Non-commercial use
- Testing and evaluation

---

## 📜 Disclaimer

All IPTV streams are sourced from publicly available playlists. Users are responsible for ensuring they have the right to access any content they stream. This software does not host or provide any copyrighted content.

---

## 📝 Changelog

### v2.0 (2024)
- ✅ Added automatic link validation
- ✅ Added Bangladesh category with multiple sources
- ✅ Added channel icons from online databases
- ✅ Added EPG support
- ✅ Added password-protected link visibility (default: `simple`)
- ✅ Added background auto-update every 5 minutes
- ✅ Added 650+ music channels
- ✅ Added professional dark theme UI
- ✅ Added right-click menu for channels
- ✅ Added copy URL functionality (password protected)
- ✅ Improved performance and stability

### v1.0 (2023)
- ✅ Initial release
- ✅ Basic IPTV player functionality
- ✅ Multiple source support
- ✅ Category filtering
- ✅ Search functionality

---

## 📞 Contact & Support

- **GitHub:** [sacuar](https://github.com/sacuar)
- **Buy Me a Coffee:** [buymeacoffee.com/sacuar](https://buymeacoffee.com/sacuar)
- **Issues:** [Report a Bug](https://github.com/sacuar/BANG-IPTV-Pro/issues)

---

## ❤️ Enjoy!

Enjoy!! :heart::heart:

---

<p align="center">
    <img src="https://raw.githubusercontent.com/sacuar/MyIPTV/main/photo/rebrand.ly.18b0e6.png" alt="QR Code" height="120">
    <br>
    <strong>BANG IPTV Pro</strong>
    <br>
    Professional IPTV Player with Auto-Validation
</p>
