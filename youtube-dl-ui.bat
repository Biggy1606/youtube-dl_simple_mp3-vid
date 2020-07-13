@echo off
:menu
cls
echo ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿
echo ³  Easy youtube-dl video/mp3 downloader  ³
echo ³  Author: Biggy1606                     ³
echo ³  bigoscloud.xyz                        ³
echo ÃÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ´
echo ³                                        ³
echo ³[1] Download MP3 (bestaudio)            ³
echo ³[2] Download VIDEO (bestvideo)          ³
echo ³[u] Update youtube-dl                   ³
echo ³[q] Quit                                ³
echo ³                                        ³
echo ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ
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
	youtube-dl.exe -x --audio-format mp3 -o "%dir%\%%(title)s-%%(abr)sKbps.%%(ext)s" -f bestaudio %link%
	echo.
	echo Downloading finished.
	goto backtomenu
:video
	call :getpath
	echo Downloading... "%link%"
	youtube-dl.exe -o "%dir%\%%(title)s-%%(abr)sKbps.%%(ext)s" -f bestvideo+bestaudio %link%
	echo.
	echo Downloading finished.
	goto backtomenu
:getpath
	set /p link="Paste link:"
	set /p dir="Set output path:"
	exit /B
:update
	youtube-dl.exe -U
	goto backtomenu
:end