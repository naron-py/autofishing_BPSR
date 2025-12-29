@echo off
setlocal

python -m pip install --upgrade pyinstaller
pyinstaller --noconsole --onefile --name start start.py

echo.
echo Build complete. Find start.exe in the "dist" folder.
pause
