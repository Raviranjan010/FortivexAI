$ErrorActionPreference = 'Stop'
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Python 3.12 is required.' }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw 'Node.js and npm are required.' }
if (-not (Test-Path '.venv')) { python -m venv .venv }
& .\.venv\Scripts\python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed.' }
& .\.venv\Scripts\python -m pip install -r backend\requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
Push-Location frontend
try { npm install; if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' } } finally { Pop-Location }
$env:PYTHONPATH = (Resolve-Path 'backend').Path
& .\.venv\Scripts\python -m app.seed
if ($LASTEXITCODE -ne 0) { throw 'Database initialization failed.' }
Write-Host 'Setup complete. Copy .env.example to .env and configure GEMINI_API_KEY.'
