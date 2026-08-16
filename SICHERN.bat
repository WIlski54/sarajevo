@echo off
rem Sichert den media-Ordner, der bewusst NICHT im Git-Repo liegt.
rem
rem Alles darin ist zwar per Skript reproduzierbar - aber die
rem Sprecherstimme kostet einen API-Lauf und die Videos kosten Renderzeit.
rem Bei einem Plattenschaden waere beides weg.
rem
rem Aufruf ohne Argument sichert nach ..\Sarajevo 1914 - Sicherung
rem Aufruf mit Argument sichert dorthin, z. B.:
rem     SICHERN.bat E:\Backup\Sarajevo

setlocal
cd /d "%~dp0"

set "ZIEL=%~1"
if "%ZIEL%"=="" set "ZIEL=%~dp0..\Sarajevo 1914 - Sicherung"

echo.
echo   Sarajevo 1914 - Mediensicherung
echo   ------------------------------------------------
echo   Von:  %~dp0media
echo   Nach: %ZIEL%\media
echo.

if not exist "%~dp0media" (
  echo   FEHLER: Es gibt noch keinen media-Ordner.
  pause
  exit /b 1
)

rem /MIR spiegelt, /NFL /NDL /NJH halten die Ausgabe kurz
robocopy "%~dp0media" "%ZIEL%\media" /MIR /R:2 /W:2 /NFL /NDL /NJH

rem robocopy meldet 0-7 als Erfolg, ab 8 sind es echte Fehler
if %ERRORLEVEL% GEQ 8 (
  echo.
  echo   FEHLER beim Kopieren ^(Code %ERRORLEVEL%^).
  pause
  exit /b 1
)

echo.
echo   Fertig. Gesichert nach:
echo   %ZIEL%\media
echo.
pause
