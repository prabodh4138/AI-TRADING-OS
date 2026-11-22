@echo off
TITLE AI Trading Operating System (AI-TOS) v3.1
cd /d "%~dp0"
echo ======================================================================
echo Starting AI Trading OS - GTF Institutional Terminal...
echo ======================================================================
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run_app.py
) else (
    python run_app.py
)
pause
