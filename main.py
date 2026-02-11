from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
import tarfile
import threading
import zipfile
from pathlib import Path
from tkinter import filedialog
from typing import Callable

import customtkinter as ctk
import requests

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
SYSTEM = platform.system().lower()
MACHINE = platform.machine().lower()

EXE_SUFFIX = ".exe" if SYSTEM == "windows" else ""
YT_DLP_BIN = APP_DIR / f"yt-dlp{EXE_SUFFIX}"
FFMPEG_BIN = APP_DIR / f"ffmpeg{EXE_SUFFIX}"
FFPROBE_BIN = APP_DIR / f"ffprobe{EXE_SUFFIX}"

DEFAULT_OUTPUT_DIR = APP_DIR / "download"

YT_DLP_PARAMS: dict[str, list[str]] = {
    "audio": ["-x", "--audio-format", "mp3", "-f", "bestaudio"],
    "video": ["-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]"],
}

FFMPEG_URLS: dict[str, str] = {
    "windows": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
    "linux": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",
    "darwin": "https://evermeet.cx/ffmpeg/getrelease/zip",
}

REQUEST_TIMEOUT = 30  # seconds for connection timeout


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _download_file(url: str, dest: Path, progress_cb: Callable[[float], None] | None = None) -> None:
    """Stream-download *url* to *dest* with optional progress callback (0..1)."""
    resp = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    with open(dest, "wb") as fh:
        for chunk in resp.iter_content(chunk_size=65_536):
            fh.write(chunk)
            downloaded += len(chunk)
            if progress_cb and total:
                progress_cb(downloaded / total)
    if progress_cb:
        progress_cb(1.0)


def _set_executable(path: Path) -> None:
    if SYSTEM != "windows":
        os.chmod(path, 0o755)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class DownloaderApp(ctk.CTk):
    """Modern yt-dlp GUI — works identically on Windows & Linux."""

    WIDTH = 560
    HEIGHT = 520

    def __init__(self) -> None:
        super().__init__()

        self.title("Media Downloader")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(480, 480)
        self.resizable(True, True)

        self._build_ui()
        self._check_tools()

    # ── UI construction ────────────────────────────────────────────
    def _build_ui(self) -> None:
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        pad = {"padx": 16, "pady": (8, 0)}

        # ── Section: Format ────────────────────────────────────────
        fmt_frame = ctk.CTkFrame(self, corner_radius=10)
        fmt_frame.grid(row=0, column=0, sticky="ew", **pad)
        fmt_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(fmt_frame, text="Format", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 4)
        )

        self._download_type = ctk.StringVar(value="audio")
        ctk.CTkRadioButton(
            fmt_frame, text="MP3  (best audio)", variable=self._download_type, value="audio"
        ).grid(row=1, column=0, padx=(16, 8), pady=4, sticky="w")
        ctk.CTkRadioButton(
            fmt_frame, text="Video  (best up to 1080p)", variable=self._download_type, value="video"
        ).grid(row=1, column=1, padx=8, pady=(4, 10), sticky="w")

        # ── Section: Download ──────────────────────────────────────
        dl_frame = ctk.CTkFrame(self, corner_radius=10)
        dl_frame.grid(row=1, column=0, sticky="ew", **pad)
        dl_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(dl_frame, text="Download", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 4)
        )

        ctk.CTkLabel(dl_frame, text="URL").grid(row=1, column=0, padx=(12, 4), pady=4, sticky="w")
        self._url_entry = ctk.CTkEntry(dl_frame, placeholder_text="Paste video or playlist URL")
        self._url_entry.grid(row=1, column=1, columnspan=2, padx=(4, 12), pady=4, sticky="ew")
        self._url_entry.bind("<KeyRelease>", self._on_url_change)

        ctk.CTkLabel(dl_frame, text="Save to").grid(row=2, column=0, padx=(12, 4), pady=4, sticky="w")
        self._path_entry = ctk.CTkEntry(dl_frame, placeholder_text=str(DEFAULT_OUTPUT_DIR))
        self._path_entry.grid(row=2, column=1, padx=(4, 4), pady=4, sticky="ew")
        self._browse_btn = ctk.CTkButton(dl_frame, text="Browse", width=70, command=self._browse_path)
        self._browse_btn.grid(row=2, column=2, padx=(0, 12), pady=4)

        self._download_btn = ctk.CTkButton(
            dl_frame, text="Download", command=self._start_download, state="disabled",
            height=36, font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._download_btn.grid(row=3, column=0, columnspan=3, padx=12, pady=(8, 4), sticky="ew")

        self._dl_progress = ctk.CTkProgressBar(dl_frame, height=6)
        self._dl_progress.grid(row=4, column=0, columnspan=3, padx=12, pady=(0, 10), sticky="ew")
        self._dl_progress.set(0)

        # ── Section: Log / Status ──────────────────────────────────
        log_frame = ctk.CTkFrame(self, corner_radius=10)
        log_frame.grid(row=2, column=0, sticky="nsew", **pad)
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(log_frame, text="Status", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 4)
        )

        self._log_box = ctk.CTkTextbox(log_frame, height=100, state="disabled", font=ctk.CTkFont(size=12))
        self._log_box.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="nsew")

        # ── Section: Tools ─────────────────────────────────────────
        tools_frame = ctk.CTkFrame(self, corner_radius=10)
        tools_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=(8, 16))
        tools_frame.grid_columnconfigure((0, 1), weight=1)

        self._ffmpeg_btn = ctk.CTkButton(tools_frame, text="Install / Update FFmpeg", command=self._start_ffmpeg_download)
        self._ffmpeg_btn.grid(row=0, column=0, padx=(12, 6), pady=10, sticky="ew")

        self._ytdlp_btn = ctk.CTkButton(tools_frame, text="Install / Update yt-dlp", command=self._start_ytdlp_download)
        self._ytdlp_btn.grid(row=0, column=1, padx=(6, 12), pady=10, sticky="ew")

        self._ffmpeg_status = ctk.CTkLabel(tools_frame, text="", font=ctk.CTkFont(size=11))
        self._ffmpeg_status.grid(row=1, column=0, padx=12, pady=(0, 8))

        self._ytdlp_status = ctk.CTkLabel(tools_frame, text="", font=ctk.CTkFont(size=11))
        self._ytdlp_status.grid(row=1, column=1, padx=12, pady=(0, 8))

    # ── Tool presence check ────────────────────────────────────────
    def _check_tools(self) -> None:
        if FFMPEG_BIN.exists():
            self._ffmpeg_status.configure(text="Installed", text_color="green")
        else:
            self._ffmpeg_status.configure(text="Not found", text_color="orange")

        if YT_DLP_BIN.exists():
            self._ytdlp_status.configure(text="Installed", text_color="green")
        else:
            self._ytdlp_status.configure(text="Not found", text_color="orange")

    # ── Logging helpers ────────────────────────────────────────────
    def _log(self, msg: str) -> None:
        """Append *msg* to the status log (thread-safe via after)."""
        def _append() -> None:
            self._log_box.configure(state="normal")
            self._log_box.insert("end", msg + "\n")
            self._log_box.see("end")
            self._log_box.configure(state="disabled")
        self.after(0, _append)

    def _set_progress(self, value: float) -> None:
        self.after(0, lambda: self._dl_progress.set(value))

    # ── URL validation ─────────────────────────────────────────────
    def _on_url_change(self, _event: object = None) -> None:
        has_text = bool(self._url_entry.get().strip())
        self._download_btn.configure(state="normal" if has_text else "disabled")

    # ── Path browser ───────────────────────────────────────────────
    def _browse_path(self) -> None:
        chosen = filedialog.askdirectory(title="Choose download folder")
        if chosen:
            self._path_entry.delete(0, "end")
            self._path_entry.insert(0, chosen)

    # ── Generic threaded task runner ───────────────────────────────
    def _run_in_thread(self, target: Callable[[], None]) -> None:
        threading.Thread(target=target, daemon=True).start()

    # ── Media download ─────────────────────────────────────────────
    def _start_download(self) -> None:
        url = self._url_entry.get().strip()
        if not url:
            return
        output_dir = self._path_entry.get().strip() or str(DEFAULT_OUTPUT_DIR)
        dl_type = self._download_type.get()

        self._download_btn.configure(state="disabled", text="Downloading...")
        self._dl_progress.set(0)

        def _task() -> None:
            try:
                if not YT_DLP_BIN.exists():
                    self._log("yt-dlp not found — install it first.")
                    return

                os.makedirs(output_dir, exist_ok=True)

                cmd = [str(YT_DLP_BIN)]
                cmd.extend(YT_DLP_PARAMS[dl_type])
                cmd.extend([
                    "--ffmpeg-location", str(APP_DIR),
                    "--newline",
                    "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
                    url,
                ])

                self._log(f"Starting {dl_type} download...")
                log.info("Running: %s", " ".join(cmd))

                creation_flags = subprocess.CREATE_NO_WINDOW if SYSTEM == "windows" else 0
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=creation_flags,
                )

                for line in proc.stdout:  # type: ignore[union-attr]
                    line = line.strip()
                    if not line:
                        continue
                    self._log(line)
                    # Parse yt-dlp progress like "[download]  45.2% ..."
                    if "[download]" in line and "%" in line:
                        try:
                            pct = float(line.split("%")[0].split()[-1]) / 100
                            self._set_progress(pct)
                        except (ValueError, IndexError):
                            pass

                proc.wait()
                if proc.returncode == 0:
                    self._log("Download completed successfully.")
                    self._set_progress(1.0)
                else:
                    self._log(f"yt-dlp exited with code {proc.returncode}.")

            except Exception as exc:
                log.exception("Download failed")
                self._log(f"Error: {exc}")
            finally:
                self.after(0, lambda: self._download_btn.configure(state="normal", text="Download"))

        self._run_in_thread(_task)

    # ── FFmpeg install ─────────────────────────────────────────────
    def _start_ffmpeg_download(self) -> None:
        self._ffmpeg_btn.configure(state="disabled", text="Downloading...")
        self._run_in_thread(self._download_ffmpeg)

    def _download_ffmpeg(self) -> None:
        """Download and extract ffmpeg + ffprobe for the current platform."""
        try:
            url = FFMPEG_URLS.get(SYSTEM)
            if url is None:
                self._log(f"Unsupported platform for FFmpeg auto-install: {SYSTEM}")
                return

            is_zip = url.endswith(".zip") or SYSTEM in ("windows", "darwin")
            archive_name = "ffmpeg.zip" if is_zip else "ffmpeg.tar.xz"
            tmp_dir = APP_DIR / "_ffmpeg_tmp"
            tmp_dir.mkdir(exist_ok=True)
            archive_path = tmp_dir / archive_name

            self._log("Downloading FFmpeg...")
            _download_file(url, archive_path, progress_cb=self._set_progress)

            self._log("Extracting FFmpeg...")
            targets = {f"ffmpeg{EXE_SUFFIX}", f"ffprobe{EXE_SUFFIX}"}

            if is_zip:
                with zipfile.ZipFile(archive_path, "r") as zf:
                    for name in zf.namelist():
                        basename = Path(name).name
                        if basename in targets:
                            zf.extract(name, tmp_dir)
                            (tmp_dir / name).rename(APP_DIR / basename)
            else:
                with tarfile.open(archive_path, "r:xz") as tf:
                    for member in tf.getmembers():
                        basename = Path(member.name).name
                        if basename in targets:
                            tf.extract(member, tmp_dir)
                            (tmp_dir / member.name).rename(APP_DIR / basename)

            shutil.rmtree(tmp_dir, ignore_errors=True)

            _set_executable(FFMPEG_BIN)
            _set_executable(FFPROBE_BIN)

            self._log("FFmpeg installed successfully.")
            self.after(0, self._check_tools)

        except Exception as exc:
            log.exception("FFmpeg download failed")
            self._log(f"FFmpeg error: {exc}")
        finally:
            shutil.rmtree(APP_DIR / "_ffmpeg_tmp", ignore_errors=True)
            self.after(0, lambda: self._ffmpeg_btn.configure(state="normal", text="Install / Update FFmpeg"))

    # ── yt-dlp install ─────────────────────────────────────────────
    def _start_ytdlp_download(self) -> None:
        self._ytdlp_btn.configure(state="disabled", text="Downloading...")
        self._run_in_thread(self._download_ytdlp)

    def _download_ytdlp(self) -> None:
        """Download the latest yt-dlp binary for the current platform."""
        try:
            filename = f"yt-dlp{EXE_SUFFIX}"
            url = f"https://github.com/yt-dlp/yt-dlp/releases/latest/download/{filename}"

            tmp_dir = APP_DIR / "_ytdlp_tmp"
            tmp_dir.mkdir(exist_ok=True)
            tmp_file = tmp_dir / filename

            self._log("Downloading yt-dlp...")
            _download_file(url, tmp_file, progress_cb=self._set_progress)

            target = APP_DIR / filename
            shutil.move(str(tmp_file), str(target))
            shutil.rmtree(tmp_dir, ignore_errors=True)

            _set_executable(target)

            self._log("yt-dlp installed successfully.")
            self.after(0, self._check_tools)

        except Exception as exc:
            log.exception("yt-dlp download failed")
            self._log(f"yt-dlp error: {exc}")
        finally:
            shutil.rmtree(APP_DIR / "_ytdlp_tmp", ignore_errors=True)
            self.after(0, lambda: self._ytdlp_btn.configure(state="normal", text="Install / Update yt-dlp"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
