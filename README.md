# SalesPilot AI

SalesPilot AI is a Windows-first, database-backed sales voice-agent prototype for the fictional B2B company NovaCRM. It combines browser speech APIs, Gemini structured generation, persistent conversation memory, document retrieval, deterministic lead qualification, an internal CRM, confirmed appointment scheduling, and real database analytics.

## Quick start

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
Copy-Item .env.example .env
# Set GEMINI_API_KEY in .env
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Open http://localhost:5173. API documentation is at http://localhost:8000/docs.

Manual fallback:

```powershell
.\.venv\Scripts\python -m app.seed --app-dir backend
.\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload --port 8000
npm --prefix frontend run dev
```

## Demo workflow

Open Live Agent, choose English or Hindi, accept the consent notice, and start. Ask about NovaCRM pricing, provide BANT details, and use text if browser recognition is unavailable. CRM, appointments, history, and analytics read actual SQLite records. An appointment API call succeeds only with explicit confirmation.

## Tests

```powershell
.\.venv\Scripts\python -m pytest backend\tests -q
npm --prefix frontend run test
npm --prefix frontend run build
```

Gemini live verification requires a valid key. Automated business tests use no hidden fake behavior in the running application. See [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md), [architecture](docs/architecture.md), and [demo script](docs/DEMO_SCRIPT.md).
