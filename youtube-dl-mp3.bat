@echo off
echo +----------------------------------+
echo +  Easy youtube-dl mp3 downloader  +
echo +  Author: Biggy1606               +
echo +----------------------------------+
set /p link=Paste link:
set /p dir=Set output path:
echo.
echo Downloading... "%link%"
youtube-dl.exe -x --audio-format mp3 -o "%dir%\%%(title)s-%%(abr)sKbps.%%(ext)s" -f bestaudio %link%
echo.
echo Downloading finished.
@pause
