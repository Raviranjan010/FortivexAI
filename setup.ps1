$ErrorActionPreference = 'Stop'
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Python 3.12 is required.' }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw 'Node.js and npm are required.' }
if (-not (Test-Path '.venv')) { python -m venv .venv }
& .\.venv\Scripts\python -m pip install --upgrade pip
& .\.venv\Scripts\python -m pip install -r backend\requirements.txt
npm --prefix frontend install
& .\.venv\Scripts\python -m app.seed --app-dir backend
Write-Host 'Setup complete. Copy .env.example to .env and configure GEMINI_API_KEY.'
