# Implementation Plan

| Milestone | Deliverable | Verification |
|---|---|---|
| 0 | Environment, architecture, persistent records | tool versions; required files |
| 1 | FastAPI/SQLite foundation and connected React shell | health/API tests; build |
| 2 | sessions, messages, memory, Gemini adapter | session/provider tests |
| 3 | browser STT/TTS state machine and fallback | frontend tests/manual browser check |
| 4 | TXT/PDF ingestion, chunk index, retrieval/sources | retrieval lifecycle tests |
| 5 | bounded tool registry, extraction, BANT, sentiment | tool/scoring tests |
| 6 | CRM and transactional confirmed scheduling | CRUD/conflict tests |
| 7 | summaries, history, database analytics | persistence/metric tests |
| 8 | responsive accessible UI and nine pages | build/manual viewport check |
| 9 | complete automation and security review | suites, scan, smoke test |
| 10 | architecture, deployment, costs, demo/interview docs | document checklist |

Priority is the complete text/voice-fallback workflow. Live Gemini and microphone verification require credentials and an interactive supported browser.
