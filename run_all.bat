@echo off
TITLE AI-TOS One-Click Master Pipeline
echo ==========================================================================
echo   AI TRADING OPERATING SYSTEM (AI-TOS) -- ONE-CLICK MASTER EXECUTION
echo   Specification v3.1 -- Simultaneous Full End-to-End Module Orchestration
echo ==========================================================================
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py --run-all
) else (
    python main.py --run-all
)

echo.
echo ==========================================================================
echo   Run completed! Press any key to exit or inspect terminal logs.
echo ==========================================================================
pause
