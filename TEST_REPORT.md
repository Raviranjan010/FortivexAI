# Test Report

Live recheck on 2026-11-26: `SALESPILOT_LIVE_TEST=1` yielded one provider unit-test pass and one credential-gated skip. Full backend: 21 passed, one skipped. Frontend: three passed, TypeScript and production build passed. Dependency check passed. The launcher reached readiness on the requested 8030/5190 ports. No live provider request was made.

Final demo checks on 2026-11-26: the opt-in provider run passed the sanitized timeout test and skipped live Gemini for lack of a key. The full backend suite passed 21 tests with one live skip. Frontend lint and all 3 tests passed. The first parallel build failed with Rolldown out of memory. An isolated build passed with `$env:RAYON_NUM_THREADS='2'`. The launcher now uses that default when no override is set. `start.ps1 -BackendPort 8030 -FrontendPort 5190 -VerifyOnly` passed backend health, proxied health and frontend HTTP readiness. `pip check` and `git diff --check` passed. The Git audit found no tracked local environment or SQLite files and no matching Google API key pattern in tracked sources. Browser and print preview checks were unavailable.

Final release rerun after the multi-round regression: 21 backend tests passed, one credential-gated test skipped. The launcher also passed on ports 8027/5187. No Google API-key pattern was found in application sources or the example environment file.

Release rerun on 2026-11-26: `$env:SALESPILOT_LIVE_TEST='1'; .\.venv\Scripts\python -m pytest backend/tests -q` produced 20 passes and 1 skipped live test. Added checks cover migration, concurrent overlapping writes, slot reuse, BANT contradictions and cached semantic retrieval with test vectors. `pip check`, frontend lint/test/build and `git diff --check` passed. Frontend had 3 passing tests and the existing bundle-size warning. `start.ps1 -BackendPort 8026 -FrontendPort 5186 -VerifyOnly` reached readiness and exited. No live provider or physical browser hardware was exercised.

Frontend redesign verification on 2026-11-25: `npm run lint` and `npm run build` passed. `npm run test` passed all 3 tests, including microphone signal scaling. Backend regression was 16 passed and 1 credential-gated skip. The Vite proxy returned a healthy database connection. Vite reported a 654.23 KB JavaScript chunk warning. Browser appearance and physical microphone behavior were not manually verified.

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
