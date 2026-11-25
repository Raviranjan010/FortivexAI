$ErrorActionPreference = 'Stop'
if (-not (Test-Path '.venv\Scripts\python.exe')) { throw 'Run setup.ps1 first.' }
$backend = Start-Process -FilePath '.\.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','app.main:app','--app-dir','backend','--port','8000' -PassThru -WindowStyle Hidden
$frontend = Start-Process -FilePath 'npm.cmd' -ArgumentList '--prefix','frontend','run','dev' -PassThru -WindowStyle Hidden
Write-Host "SalesPilot started: frontend http://localhost:5173 backend http://localhost:8000/docs"
Write-Host "Process IDs: backend $($backend.Id), frontend $($frontend.Id). Press Enter to stop both."
Read-Host
Stop-Process -Id $backend.Id,$frontend.Id -ErrorAction SilentlyContinue
