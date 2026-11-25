param(
    [ValidateRange(1024,65535)][int]$BackendPort = 8000,
    [ValidateRange(1024,65535)][int]$FrontendPort = 5173,
    [switch]$VerifyOnly
)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
function Assert-PortFree([int]$Port) {
    $listener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, $Port)
    try { $listener.Server.ExclusiveAddressUse = $true; $listener.Start() }
    catch { throw "Port $Port is unavailable. Select another port." }
    finally { $listener.Stop() }
}
function Wait-Ready($Process, [string]$Url) {
    $deadline = (Get-Date).AddSeconds(20)
    do {
        if ($Process.HasExited) { throw "Service exited before readiness: $Url" }
        try {
            $health = Invoke-RestMethod -Uri $Url -TimeoutSec 2
            if ($health.service -eq 'SalesPilot AI' -and $health.database -eq 'connected') { return }
        } catch {}
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $deadline)
    throw "Service did not become ready: $Url"
}
if ($BackendPort -eq $FrontendPort) { throw 'Use different frontend and backend ports.' }
Assert-PortFree $BackendPort
Assert-PortFree $FrontendPort
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$vite = Join-Path $PSScriptRoot 'frontend\node_modules\vite\bin\vite.js'
if (!(Test-Path $python) -or !(Test-Path $vite)) { throw 'Run setup.ps1 first.' }
$node = (Get-Command node.exe).Source
$backend = $frontend = $null
$previous = $env:SALESPILOT_BACKEND_URL
$previousThreadLimit = $env:RAYON_NUM_THREADS
try {
    $env:SALESPILOT_BACKEND_URL = "http://127.0.0.1:$BackendPort"
    if (!$env:RAYON_NUM_THREADS) { $env:RAYON_NUM_THREADS = '2' }
    $backend = Start-Process $python -ArgumentList '-m','uvicorn','app.main:app','--app-dir','backend','--host','127.0.0.1','--port',"$BackendPort" -PassThru -WindowStyle Hidden
    Wait-Ready $backend "$env:SALESPILOT_BACKEND_URL/api/health"
    $frontend = Start-Process $node -WorkingDirectory (Join-Path $PSScriptRoot 'frontend') -ArgumentList 'node_modules/vite/bin/vite.js','--host','127.0.0.1','--port',"$FrontendPort",'--strictPort' -PassThru -WindowStyle Hidden
    $frontendUrl = "http://127.0.0.1:$FrontendPort"
    Wait-Ready $frontend "$frontendUrl/api/health"
    $null = Invoke-WebRequest -Uri $frontendUrl -UseBasicParsing -TimeoutSec 5
    Write-Host "SalesPilot ready at $frontendUrl. API docs at $env:SALESPILOT_BACKEND_URL/docs."
    if (!$VerifyOnly) { $null = Read-Host 'Press Enter to stop SalesPilot' }
} finally {
    foreach ($process in @($frontend, $backend)) {
        if ($process -and !$process.HasExited) { Stop-Process -InputObject $process -ErrorAction SilentlyContinue }
    }
    $env:SALESPILOT_BACKEND_URL = $previous
    $env:RAYON_NUM_THREADS = $previousThreadLimit
}
