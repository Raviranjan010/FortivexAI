# Test Report

No tests have run yet. This file records commands, dates, pass/fail counts, and whether dependencies are real, test doubles, or manually verified.

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
