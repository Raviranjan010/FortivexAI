# Test Report

The local API workflow uses a deterministic provider double. Live Gemini is tracked separately.

The follow-up workflow test exercised retrieval, lead storage and scoring, proposal generation, model confirmation rejection, cross-session rejection, customer confirmation, idempotency, summary, and analytics. Vite forwarded live health and config requests to FastAPI on port 8011, which reported `ai_configured=false`.

Follow-up rerun on 2026-11-25: 13 backend tests passed, 1 credential-gated live test skipped, 2 frontend tests passed, and TypeScript/Vite production build passed with a bundle-size warning. `git diff --check` passed. To opt in when a key is configured, set `$env:SALESPILOT_LIVE_TEST='1'` and run `.\.venv\Scripts\python -m pytest backend/tests/test_provider.py -q`.

| Date | Scope | Command | Result | Evidence |
|---|---|---|---|---|
| 2026-11-25 | Environment | version inspection | PASS | Python 3.12.10; Node 22.20.0; npm 10.9.3 |
| 2026-11-25 | Backend | `.venv\Scripts\python -m pytest backend\tests -q` | PASS | 11 passed; 1 upstream deprecation warning; deterministic local services |
| 2026-11-25 | Frontend logic | `npm run test` | PASS | 1 file, 2 state-machine tests passed |
| 2026-11-25 | Production build | `npm run build` | PASS | 2,749 modules; 664.72 KB JS; bundle-size warning only |
| 2026-11-25 | Dependency audit | `npm install` audit | PASS | 0 vulnerabilities reported |
| 2026-11-25 | Secret scan | repository regex scan | PASS | No Gemini key patterns found |
| 2026-11-25 | API smoke | Uvicorn on port 8011 + health/config requests | PASS | health `ok`, database `connected`, `ai_configured=false` |
| 2026-11-25 | Live Gemini | Requires credential | NOT RUN | No `GEMINI_API_KEY`; automated tests do not claim provider verification |
| 2026-11-25 | Browser voice | Interactive Chromium/hardware | NOT RUN | Manual English/Hindi STT/TTS check required |
| 2026-11-25 | Playwright E2E | Browser environment | NOT RUN | Exact manual workflow in `docs/DEMO_SCRIPT.md` |
