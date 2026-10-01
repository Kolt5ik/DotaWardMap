@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe goto missing
.venv\Scripts\python.exe -m streamlit run app.py
pause
exit /b
:missing
echo Please follow Windows installation steps in README.md first.
pause
