@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
 python -m venv .venv
 if errorlevel 1 goto fail
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install "pyinstaller>=6.10,<7"
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean dota_ward_map.spec
if errorlevel 1 goto fail
echo EXE: %CD%\dist\DotaWardMap.exe
pause
exit /b 0
:fail
echo Build failed. Read the error above.
pause
exit /b 1
