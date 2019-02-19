@echo off
echo +----------------------------------------+
echo +  Easy youtube-dl video/mp3 downloader  +
echo +  Author: Biggy1606                     +
echo +----------------------------------------+
echo [1] Download mp3
echo [2] Download video
set /p selection=
echo.
if %selection% == 1 (
	set /p link="Paste link:"
	set /p dir="Set output path:"
	echo.
	echo Downloading... "%link%"
	youtube-dl.exe -x --audio-format mp3 -o "%dir%\%%(title)s-%%(abr)sKbps.%%(ext)s" -f bestaudio %link%
	echo.
	echo Downloading finished.
)
if %selection% == 2 (
	set /p link="Paste link:"
	set /p dir="Set output path:"
	echo.
	echo Downloading... "%link%"
	youtube-dl.exe -o "%dir%\%%(title)s-%%(abr)sKbps.%%(ext)s" -f bestvideo+bestaudio %link%
	echo.
	echo Downloading finished.
)
@pause
