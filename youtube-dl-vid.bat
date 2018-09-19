@echo off
echo +------------------------------------+
echo +  Easy youtube-dl video downloader  +
echo +  Author: Biggy1606                 +
echo +------------------------------------+
set /p link=Paste link:
set /p dir=Set output path:
echo.
echo Downloading... "%link%"
youtube-dl.exe -o "%dir%\%%(title)s-%%(abr)sKbps.%%(ext)s" -f bestvideo+bestaudio %link%
echo.
echo Downloading finished.
@pause
