# 🎬 BANG IPTV Pro

<div align="center">
    <img src="screenshots/icon.png" alt="BANG IPTV Pro" width="200">
    <br>
    <h3>Professional IPTV Player with Auto-Validation</h3>
    <p>Bangladesh Category · EPG Support · Music Channels · Auto-Link Validation</p>
</div>

---

## 📢 Announcement

### 🚀 BANG IPTV Pro v2.0 - Happy New Release!

I'm excited to announce the release of **BANG IPTV Pro v2.0** - a professional IPTV player with automatic link validation, Bangladesh category support, channel icons, and EPG integration.

---

## 📸 Screenshots
<img width="2560" height="1600" alt="image" src="https://github.com/user-attachments/assets/9c206626-7719-4c02-90fa-31014b3864bb" />

### Main Interface - World IPTV
<p align="center">
    <img src="<img width="2560" height="1600" alt="image" src="https://github.com/user-attachments/assets/01cf642b-89ab-4aad-88ff-b779081958ed" />
</p>

### Bangladesh Channels
<p align="center">
    <img src="screenshots/screenshot2.png" width="800" alt="Bangladesh Channels">
</p>

---

## 📺 Features

| Feature | Status | Description |
|---------|--------|-------------|
| 🔗 **Auto Link Validation** | ✅ | Automatically checks and marks working/dead links |
| 🇧🇩 **Bangladesh Category** | ✅ | Dedicated BD channels from multiple sources |
| 🖼️ **Channel Icons** | ✅ | Fetches icons from online databases |
| 📅 **EPG Support** | ✅ | Electronic Program Guide integration |
| 🔒 **Password Protection** | ✅ | Default password: `simple` - Ctrl+L to reveal links |
| 🔄 **Auto-Update** | ✅ | Background link validation every 5 minutes |
| 📺 **Professional UI** | ✅ | Dark theme, right-click menu, status indicators |
| 🎵 **Music Channels** | ✅ | 650+ music channels from iptv-org |
| 🎬 **Movie Channels** | ✅ | Dedicated movie category |
| ⚽ **Sports Channels** | ✅ | Sports channels worldwide |
| 📰 **News Channels** | ✅ | News channels worldwide |

---

## 📦 Sources Included

| Source | Description | Channels |
|--------|-------------|----------|
| 🌍 **World IPTV** | Free-TV IPTV collection | 5,000+ |
| 📺 **Global TV** | iptv-org official playlist | 10,000+ |
| 🇧🇩 **Bangladesh IPTV** | Bangladeshi channels | 200+ |
| 🇧🇩 **BDIX IPTV** | BDIX supported channels | 600+ |
| 🇧🇩 **Bangladesh (iptv-org)** | Official BD channels | 100+ |
| 🇬🇧 **UK Free** | UK free channels | 500+ |
| 🇺🇸 **US Free** | US free channels | 500+ |
| 📰 **News** | News worldwide | 1,000+ |
| ⚽ **Sports** | Sports channels | 500+ |
| 🎵 **Music** | Music channels | 650+ |
| 🎬 **Movies** | Movie channels | 300+ |

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
9. **Right-click** a channel for options (Copy URL, Info)

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

## 📞 Contact & Support

- **GitHub:** [sacuar](https://github.com/sacuar)
- **Buy Me a Coffee:** [buymeacoffee.com/sacuar](https://buymeacoffee.com/sacuar)
- **Issues:** [Report a Bug](https://github.com/sacuar/BANG-IPTV-Pro/issues)

---

## ❤️ Enjoy!

Enjoy!! :heart::heart:

---

<div align="center">
    <strong>BANG IPTV Pro</strong>
    <br>
    Professional IPTV Player with Auto-Validation
    <br><br>
    Made with ❤️ by <strong>sacuar</strong>
</div>
