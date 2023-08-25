@echo off
:menu
cls
echo ����������������������������������������Ŀ
echo �  Easy yt-dlp video/mp3 downloader  �
echo �  Author: Biggy1606                     �
echo �  bigoscloud.xyz                        �
echo ����������������������������������������Ĵ
echo �                                        �
echo �[1] Download MP3 (bestaudio)            �
echo �[2] Download VIDEO (bestvideo)          �
echo �[u] Update yt-dlp                   �
echo �[q] Quit                                �
echo �                                        �
echo ������������������������������������������
set /p selection=Select: 
if %selection% == 1 ( goto audio )
if %selection% == 2 ( goto video )
if /I %selection% == q ( goto end )
if /I %selection% == u ( goto update 
) else ( 
	echo Bad option!
	goto backtomenu
)
:backtomenu
	echo Press any key to back to menu...
	PAUSE >nul
	goto menu
:audio
	call :getpath
	echo Downloading... "%link%"
	yt-dlp.exe -x --audio-format mp3 -o "%dir%\%%(title)s-%%(abr)sKbps.%%(ext)s" -f bestaudio %link%
	echo.
	echo Downloading finished.
	goto backtomenu
:video
	call :getpath
	echo Downloading... "%link%"
	yt-dlp.exe -o "%dir%\%%(title)s-%%(abr)sKbps.%%(ext)s" -f bestvideo+bestaudio %link%
	echo.
	echo Downloading finished.
	goto backtomenu
:getpath
	set /p link="Paste link:"
	set /p dir="Set output path:"
	exit /B
:update
	yt-dlp.exe -U
	goto backtomenu
:end