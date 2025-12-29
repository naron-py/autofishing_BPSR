@echo off
setlocal
cd /d "%~dp0"

if /i "%~1"=="elevated" goto :run
powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs -ArgumentList 'elevated'" 1>nul 2>nul
exit /b

:run
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 main.py
) else (
  python main.py
)

pause
