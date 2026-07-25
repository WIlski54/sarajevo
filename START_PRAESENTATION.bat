@echo off
title Sarajevo 1914 - Praesentation
cd /d "%~dp0"
echo.
echo   Sarajevo 1914 - Cinematic Live-Praesentation
echo   ------------------------------------------------
echo   Der Browser oeffnet sich in wenigen Sekunden.
echo   Dieses Fenster bitte offen lassen.
echo   Beenden: dieses Fenster schliessen oder Strg+C.
echo.
python tools\serve.py
if errorlevel 1 (
  echo.
  echo   FEHLER: Python wurde nicht gefunden oder der Port ist belegt.
  echo   Pruefen mit:  python --version
  pause
)
