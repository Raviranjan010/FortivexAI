# SalesPilot AI Engineering Guide

## Mission
Build a reliable Windows-first NovaCRM sales-agent demonstration. Never report a business action unless the database records it. External AI and browser voice capabilities must be labelled unverified until exercised with credentials/hardware.

## Architecture
- `backend/app`: modular FastAPI application; routers -> services -> SQLAlchemy models.
- `frontend/src`: React/TypeScript UI using one centralized API client.
- SQLite is the local source of truth. Store UTC timestamps and render in the configured timezone.
- Gemini is accessed only through `AIProvider`; deterministic fakes exist only in tests.
- RAG uses persisted, local TF-IDF/cosine retrieval to avoid a heavyweight native dependency on Windows while preserving true chunked semantic retrieval.

## Rules
- Validate API payloads with Pydantic and tool inputs with explicit schemas.
- Appointment creation requires backend-validated explicit confirmation and a transaction.
- BANT scores are deterministic (25 points per category); unknown values score zero.
- No API keys in source, logs, responses, or frontend storage.
- Preserve session isolation; never fetch messages without the session key.
- Do not expose chain-of-thought. Only observable tool events are returned.
- All visible primary controls must call real behavior or be clearly disabled with explanation.

## Conventions
- Python: typed functions, UTC-aware datetimes, snake_case, services kept independent of HTTP.
- TypeScript: strict mode, functional components, centralized types/API client.
- Tests use temporary SQLite databases and deterministic provider doubles.
- Update `PROGRESS.md` and `TEST_REPORT.md` after each verified milestone.

## Commands
- Setup: `powershell -ExecutionPolicy Bypass -File .\setup.ps1`
- Backend: `.\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload --port 8000`
- Frontend: `npm --prefix frontend run dev`
- Backend tests: `.\.venv\Scripts\python -m pytest backend/tests -q`
- Frontend checks: `npm --prefix frontend run test` and `npm --prefix frontend run build`

## Quality Gate
Run backend tests, frontend tests/typecheck, production build, health smoke test, secret scan, and a core-workflow integration test. Record exact results and limitations.
