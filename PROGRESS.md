# Progress

The frontend redesign makes Live Voice Agent the default workspace. It adds a Web Audio input meter, transcript and activity panels, customer details, lead score meters, CRM search, and a date-filtered appointment agenda. Real microphone and visual browser verification remain open.

## Completed
- Milestone 0: inspected clean workspace and validated Python 3.12.10, Node 22.20.0, npm 10.9.3.
- Defined modular-monolith architecture and persistent engineering rules.
- Milestone 1: FastAPI/SQLite foundation and Vite API routing passed a live smoke check.
- Automated verification: 13 backend tests passed, 1 live test skipped, 2 frontend tests passed, and the production build passed. Browser and live provider gates are open.
- Milestone 10: required architecture, security, deployment, scalability, cost, demo, API, report, and interview documentation.

## Current
- Re-audit identified Milestone 2 as the first incomplete milestone. Added provider error handling and an opt-in live test. Live credentials are absent.
- Hardened Milestone 6 confirmation. A persisted proposal can be confirmed only through a separate customer action bound to the conversation.
- Verified Vite-to-FastAPI routing on ports 5173 and 8011. Port 8000 timed out.

## Remaining
- Semantic embeddings, browser voice checks and microphone activity, richer CRM details and UI filters, rescheduling, and browser E2E.
- Configure a valid Gemini key and run the separately identified live provider workflow.
- Verify microphone permission, English/Hindi recognition, and synthesis in interactive Chromium.
- Add Playwright browser automation when a supported browser environment is available.

## Failed Tests
- Initial run: retrieval morphology and missing Windows timezone database (resolved; rerun passed).
- Initial frontend build: Vite declarations and React 19 ref initializers (resolved; rerun passed).

## Issues
- Windows `py` launcher is unavailable; scripts use `python`.
- Port 8000 was occupied and unresponsive during final smoke testing; verified SalesPilot on port 8011 without terminating the unknown process.
- Gemini is not configured; live provider and browser microphone remain unverified.

## Resolved Issues
- Selected lightweight persisted TF-IDF retrieval to reduce Windows native dependency risk.
- Added `tzdata` for reliable IANA timezone handling on Windows.
- Corrected Windows npm working-directory and Python module-path setup behavior.

## Next Action
Use `start.ps1 -BackendPort 8011` if 8000 is occupied. Run the opt-in Gemini test once a credential is available and continue with the remaining browser and product criteria.
