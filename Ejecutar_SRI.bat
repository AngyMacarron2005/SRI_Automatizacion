@echo off
title Robot SRI - Finetic C.L.
cd /d "%~dp0"
call .\venv\Scripts\activate.bat
python sri_bot.py
pause
