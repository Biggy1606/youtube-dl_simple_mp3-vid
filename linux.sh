#!/bin/bash
echo +----------------------------------------+
echo +  Easy youtube-dl video/mp3 downloader  +
echo +  Author: Biggy1606                     +
echo +----------------------------------------+
echo [1] Download mp3
echo [2] Download video
echo
if [warunek]
then
	zgarnij link
	zgarnij sciezke
	echo
	echo Downloading... <link>
	youtube-dl.exe -x --audio-format mp3 -o <sciezka>/'%(title)s-%(abr)sKbps.%(ext)s' -f bestaudio <link>
	echo
	echo Download finished.
fi
if [warunek]
then
	zgarnij link
	zgarnij sciezka
	
	echo Choose quality:
	echo [1] Best (mostly webm)
	echo [2] Good (mp4)

	if [warunek best]
	then
		<zmienna> = 
	fi

	if [warunek mp4]
	then
		<zmienna> = "--format mp4"
	fi

	echo Downloading... <link>
	youtube-dl.exe -o <sciezka>/'%(title)s-%(abr)sKbps.%(ext)s" -f bestvideo+bestaudio %link%
