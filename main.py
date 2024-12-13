import subprocess
import os
import platform
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import zipfile
import tarfile


class DownloaderApp:
    YT_DLP_PARAMS = {
        "audio": "-x --audio-format mp3 -f bestaudio",
        "video": "-f bestvideo+bestaudio",
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Downloader Tool")
        self.root.geometry("400x320")
        self.root.minsize(400, 320)

        # Configure grid weights to make window dynamic
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(1, weight=1)

        # Create radio buttons for download type at the top
        self.download_type = tk.StringVar(value="audio")
        audio_radio = ttk.Radiobutton(
            main_frame,
            text="Download MP3 (best audio)",
            variable=self.download_type,
            value="audio",
        )
        video_radio = ttk.Radiobutton(
            main_frame,
            text="Download VIDEO (best video max 1080p)",
            variable=self.download_type,
            value="video",
        )
        audio_radio.grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky=tk.W)
        video_radio.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky=tk.W)

        # Create URL entry field with validation
        url_label = ttk.Label(main_frame, text="URL:")
        url_label.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.url_entry = ttk.Entry(main_frame, width=40)
        self.url_entry.grid(row=2, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))
        self.url_entry.bind("<KeyRelease>", self.validate_url)

        # Create path entry field
        path_label = ttk.Label(main_frame, text="Path (empty = app location):")
        path_label.grid(row=3, column=0, pady=5, padx=5, sticky=tk.W)
        self.path_entry = ttk.Entry(main_frame, width=40)
        self.path_entry.grid(row=3, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))

        # Create download button
        self.download_button = ttk.Button(
            main_frame, text="Download", command=self.start_download, state="disabled"
        )
        self.download_button.grid(
            row=4, column=0, columnspan=2, pady=10, padx=10, sticky=(tk.W, tk.E)
        )

        # Add separator
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.grid(row=5, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        # Create buttons
        self.ffmpeg_button = ttk.Button(
            main_frame,
            text="Download/Update FFmpeg",
            command=self.start_ffmpeg_download,
        )
        self.ffmpeg_button.grid(
            row=6, column=0, columnspan=2, pady=10, padx=10, sticky=(tk.W, tk.E)
        )

        self.ytdlp_button = ttk.Button(
            main_frame,
            text="Download/Update yt-dlp",
            command=self.start_ytdlp_download,
        )
        self.ytdlp_button.grid(
            row=7, column=0, columnspan=2, pady=10, padx=10, sticky=(tk.W, tk.E)
        )

    def validate_url(self, event=None):
        if self.url_entry.get().strip():
            self.download_button["state"] = "normal"
        else:
            self.download_button["state"] = "disabled"

    def start_download(self):
        self.download_button["state"] = "disabled"
        self.download_button["text"] = "Downloading ⟳"
        url = self.url_entry.get().strip()
        output_path = self.path_entry.get().strip() or "./download"
        download_type = self.download_type.get()

        def download_thread():
            try:
                # Create download directory if it doesn't exist
                os.makedirs(output_path, exist_ok=True)

                # Build command
                cmd = ["./yt-dlp"]
                cmd.extend(self.YT_DLP_PARAMS[download_type].split())
                cmd.extend(
                    [
                        "-o",
                        os.path.join(output_path, "%(title)s-%(abr)sKbps.%(ext)s"),
                        url,
                    ]
                )

                subprocess.run(cmd, check=True)

                self.root.after(
                    0, lambda: messagebox.showinfo("Success", "Download completed!")
                )
            except Exception as error:
                self.root.after(
                    0, lambda error=error: messagebox.showerror("Error", str(error))
                )
            finally:
                self.root.after(
                    0,
                    lambda: self.download_button.configure(
                        state="normal", text="Download"
                    ),
                )

        threading.Thread(target=download_thread, daemon=True).start()

    def get_platform_info(self):
        system = platform.system().lower()
        machine = platform.machine().lower()
        return system, machine

    def start_ffmpeg_download(self):
        self.ffmpeg_button.state(["disabled"])
        self.ffmpeg_button["text"] = "Downloading FFmpeg ⟳"
        thread = threading.Thread(target=self.download_ffmpeg)
        thread.daemon = True
        thread.start()

    def start_ytdlp_download(self):
        self.ytdlp_button.state(["disabled"])
        self.ytdlp_button["text"] = "Downloading yt-dlp ⟳"
        thread = threading.Thread(target=self.download_ytdlp)
        thread.daemon = True
        thread.start()

    def download_ffmpeg(self):
        """
        Process:
        1. Determine OS and machine architecture
        2. Set download URLs based on OS
        3. Download FFmpeg archive file
        4. Extract only ffmpeg and ffprobe executables
        5. Clean up archive, empty directories and move executables to bin folder
        6. Set proper permissions on Unix systems
        7. Update UI with status
        """
        try:
            # Step 1: Determine OS and machine architecture
            system, machine = self.get_platform_info()

            # Step 2: Set download URLs based on OS
            if system == "windows":
                url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
                archive_name = "ffmpeg.zip"
                exe_suffix = ".exe"
            elif system == "darwin":
                url = "https://evermeet.cx/ffmpeg/ffmpeg-5.1.zip"
                archive_name = "ffmpeg.zip"
                exe_suffix = ""
            elif system == "linux":
                url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
                archive_name = "ffmpeg.tar.xz"
                exe_suffix = ""

            # Step 3: Download FFmpeg archive file
            response = requests.get(url, stream=True)
            download_path = Path("./ffmpeg-download")
            download_path.mkdir(exist_ok=True)
            archive_path = download_path / archive_name

            with open(archive_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Step 4: Extract only ffmpeg and ffprobe executables
            if archive_name.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "r") as zip_ref:
                    for file in zip_ref.namelist():
                        if file.endswith(f"ffmpeg{exe_suffix}") or file.endswith(
                            f"ffprobe{exe_suffix}"
                        ):
                            zip_ref.extract(file, download_path)
                            source = download_path / file
                            target = Path(".") / file.split("/")[-1]
                            source.rename(target)
            elif archive_name.endswith(".tar.xz"):
                with tarfile.open(archive_path, "r:xz") as tar_ref:
                    for member in tar_ref.getmembers():
                        if member.name.endswith("ffmpeg") or member.name.endswith(
                            "ffprobe"
                        ):
                            tar_ref.extract(member, download_path)
                            source = download_path / member.name
                            target = Path(".") / member.name.split("/")[-1]
                            source.rename(target)

            # Step 5: Clean up archive and empty directories
            archive_path.unlink()
            for root, dirs, files in os.walk(download_path, topdown=False):
                for dir in dirs:
                    dir_path = Path(root) / dir
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
            download_path.rmdir()

            # Step 6: Set proper permissions on Unix systems
            if system != "windows":
                os.chmod(Path(".") / "ffmpeg", 0o755)
                os.chmod(Path(".") / "ffprobe", 0o755)

            # Step 7: Update UI with status
            self.root.after(0, lambda: self.ffmpeg_button.state(["!disabled"]))
            self.root.after(
                0, lambda: self.ffmpeg_button.configure(text="Download/Update FFmpeg")
            )
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success", "FFmpeg downloaded and extracted successfully!"
                ),
            )

        except Exception as e:
            self.root.after(0, lambda: self.ffmpeg_button.state(["!disabled"]))
            self.root.after(
                0, lambda: self.ffmpeg_button.configure(text="Download/Update FFmpeg")
            )
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Error", f"Failed to download FFmpeg: {str(e)}"
                ),
            )

    def download_ytdlp(self):
        """
        Process:
        1. Determine OS and machine architecture
        2. Set download URLs based on OS
        3. Download yt-dlp executable
        4. Move executable to bin folder
        5. Set proper permissions on Unix systems
        6. Update UI with status
        """
        try:
            # Step 1: Determine OS and machine architecture
            system, machine = self.get_platform_info()

            # Step 2: Set download URLs based on OS
            filename = "yt-dlp.exe" if system == "windows" else "yt-dlp"
            url = (
                f"https://github.com/yt-dlp/yt-dlp/releases/latest/download/{filename}"
            )

            # Step 3: Download yt-dlp executable
            response = requests.get(url, stream=True)
            download_path = Path("./yt-dlp-download")
            download_path.mkdir(exist_ok=True)
            temp_file = download_path / filename

            with open(temp_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Step 4: Move executable to bin folder
            target_file = Path(".") / filename
            temp_file.rename(target_file)
            download_path.rmdir()

            # Step 5: Set proper permissions on Unix systems
            if system != "windows":
                os.chmod(target_file, 0o755)

            # Step 6: Update UI with status
            self.root.after(0, lambda: self.ytdlp_button.state(["!disabled"]))
            self.root.after(
                0, lambda: self.ytdlp_button.configure(text="Download/Update yt-dlp")
            )
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success", "yt-dlp downloaded successfully!"
                ),
            )

        except Exception as e:
            self.root.after(0, lambda: self.ytdlp_button.state(["!disabled"]))
            self.root.after(
                0, lambda: self.ytdlp_button.configure(text="Download/Update yt-dlp")
            )
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Error", f"Failed to download yt-dlp: {str(e)}"
                ),
            )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DownloaderApp()
    app.run()
