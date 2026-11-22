# AI-TOS One-Click Master Pipeline Launcher (PowerShell)
# Simultaneously executes all modules: Download -> DB Sync -> MTF Zones -> ML Scan -> Fundamentals -> Risk Gate -> Paper Trading -> Report
param(
    [switch]$Dashboard
)

$Host.UI.RawUI.WindowTitle = "AI-TOS One-Click Master Pipeline"
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "  ⚡ AI TRADING OPERATING SYSTEM (AI-TOS) -- ONE-CLICK MASTER PIPELINE" -ForegroundColor Cyan
Write-Host "  Consolidated Planning Specification v3.1 | Indian Equity Paper Platform" -ForegroundColor DarkCyan
Write-Host "==========================================================================" -ForegroundColor Cyan

$PythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

if ($Dashboard) {
    & $PythonExe main.py --run-all --dashboard
} else {
    & $PythonExe main.py --run-all
}
