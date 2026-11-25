param([ValidateRange(1024,65535)][int]$BackendPort = 8000)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path '.venv\Scripts\python.exe')) { throw 'Run setup.ps1 first.' }
$env:SALESPILOT_BACKEND_URL = "http://127.0.0.1:$BackendPort"
$backend = Start-Process -FilePath '.\.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','app.main:app','--app-dir','backend','--port',"$BackendPort" -PassThru -WindowStyle Hidden
$frontend = Start-Process -FilePath 'npm.cmd' -WorkingDirectory (Resolve-Path 'frontend').Path -ArgumentList 'run','dev','--','--strictPort' -PassThru -WindowStyle Hidden
Write-Host "SalesPilot URLs: frontend http://localhost:5173 backend http://localhost:${BackendPort}/docs"
Write-Host "Process IDs: backend $($backend.Id), frontend $($frontend.Id). Press Enter to stop both."
Read-Host
Stop-Process -Id $backend.Id,$frontend.Id -ErrorAction SilentlyContinue
