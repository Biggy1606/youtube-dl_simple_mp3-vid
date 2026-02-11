# Media Downloader

A simple GUI tool for downloading audio (MP3) and video from the web using [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Features

- **Modern dark/light UI** — adapts to your system theme
- **MP3 or Video** — best audio or best video up to 1080p
- **Live progress** — real-time progress bar and status log
- **One-click tool install** — download yt-dlp and FFmpeg directly from the app
- **Cross-platform** — Windows and Linux

## Requirements

- **Python 3.10+** with `tkinter` (included on Windows; on Linux install `python3-tk`)

Everything else (virtualenv, dependencies, yt-dlp, FFmpeg) is handled automatically.

## Quick Start

### Windows — double-click `run.bat`

Or from a terminal:

```cmd
run.bat
```

### Windows — PowerShell

```powershell
.\run.ps1
```

### Linux / macOS

```bash
chmod +x run.sh
./run.sh
```

The launcher script will:

1. Create a `.venv` virtual environment (if missing)
2. Install Python dependencies from `requirements.txt`
3. Launch the GUI

Once the app is open, use the **Install / Update** buttons at the bottom to fetch `yt-dlp` and `FFmpeg`.

## Project Structure

```
├── main.py            # Application source
├── requirements.txt   # Python dependencies
├── run.bat            # Windows CMD launcher
├── run.ps1            # PowerShell launcher (Windows / Linux / macOS)
├── run.sh             # Bash launcher (Linux / macOS)
├── LICENSE
└── README.md
```

## Changelog

- **v2.0** — Full rewrite: modern CustomTkinter UI, cross-platform fixes, progress bars, live log, one-click tool install
- **v1.5** — Changed structure of Windows script, fixed basic functions, added update yt-dlp option
- **v1.1** — Merged scripts into one, started Linux bash script
- **v1.0** — Separate scripts for video and MP3
