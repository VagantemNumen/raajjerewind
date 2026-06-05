#!/usr/bin/env pwsh
# Launch backend (uvicorn) and frontend (vite) dev servers in separate windows.

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$venvPython = Join-Path $root '.venv\Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
    Write-Error "Python venv not found at $venvPython. Create it: python -m venv .venv ; .venv\Scripts\Activate.ps1 ; pip install -r backend\requirements.txt"
    exit 1
}

if (-not (Test-Path (Join-Path $root 'frontend\node_modules'))) {
    Write-Error "Frontend deps not installed. Run: cd frontend ; npm install"
    exit 1
}

$backendCmd  = "Set-Location '$root\backend'; & '$venvPython' -m uvicorn main:app --reload"
$frontendCmd = "Set-Location '$root\frontend'; npm run dev"

Start-Process pwsh -ArgumentList @('-NoExit', '-Command', $backendCmd)
Start-Process pwsh -ArgumentList @('-NoExit', '-Command', $frontendCmd)

Write-Host "Backend:  http://127.0.0.1:8000"
Write-Host "Frontend: http://127.0.0.1:5173"
