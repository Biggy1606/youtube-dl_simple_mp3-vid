#!/usr/bin/env bash
# Media Downloader — Linux / macOS launcher
set -euo pipefail
cd "$(dirname "$0")"

# --- Check Python ------------------------------------------------------------
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 is not installed."
    echo "        Install via your package manager:"
    echo "          Ubuntu/Debian : sudo apt install python3 python3-venv python3-tk"
    echo "          Fedora        : sudo dnf install python3 python3-tkinter"
    echo "          macOS         : brew install python python-tk"
    exit 1
fi

# --- Check tkinter available -------------------------------------------------
if ! python3 -c "import tkinter" &>/dev/null; then
    echo "[ERROR] python3-tkinter is not installed."
    echo "        Install via your package manager:"
    echo "          Ubuntu/Debian : sudo apt install python3-tk"
    echo "          Fedora        : sudo dnf install python3-tkinter"
    echo "          macOS         : brew install python-tk"
    exit 1
fi

# --- Create venv if missing --------------------------------------------------
if [ ! -f ".venv/bin/python" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv .venv
fi

# --- Install / update dependencies -------------------------------------------
echo "[*] Checking dependencies..."
.venv/bin/pip install -q -r requirements.txt

# --- Launch ------------------------------------------------------------------
echo "[*] Starting Media Downloader..."
.venv/bin/python main.py
