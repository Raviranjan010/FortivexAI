# SalesPilot AI assessment readiness audit

## Release follow-up on 2026-11-26

The historical findings below describe the earlier audit. The release now guards interval overlap in SQLite, reopens cancelled slots, preserves legacy appointment rows, and attributes conversion and summary bookings to originating proposals. Structured tool execution runs across bounded rounds. Optional Gemini embeddings and model sentiment are implemented. Provider credentials, browser hardware, Playwright and rescheduling remain outstanding. See `RELEASE_COVERAGE.md` and `TEST_REPORT.md` for current status.

Audit date: 2026-11-25. Reviewed the original specification, engineering rules, acceptance checklist, progress and prior test results against the current frontend, backend, local database, AI adapter, tools, and demo documentation. Re-ran verification from the working tree.

## Readiness

Ready for a limited local engineering walkthrough using fictional data. Full technical assessment readiness is conditional on a successful live Gemini and browser microphone run. The automated customer journey uses a deterministic provider double and exercises the real API, retrieval, ORM and business rules. A fresh Vite and FastAPI smoke run served the page and reached the database through the proxy. The browser customer journey and restart persistence were not independently verified during this audit.

## Findings and fixes

| Severity | Finding and root cause | Disposition |
|---|---|---|
| High | Slot search compared only start timestamps. Changing slot length could expose part of an existing booking. | Compared complete intervals. Regression verifies a conflicting booking is rejected after a duration change. SQLite uniqueness still covers exact starts only. |
| High | Conversation and CRM APIs have no caller authentication. A session ID scopes queries but does not establish authorization. | Open. Loopback and fictional data only. Authentication and per-record authorization are needed before shared deployment. |
| High | Untrusted transcripts and document excerpts enter the model prompt. Its tool choices can update CRM records. | Existing allow-list and argument validation constrain tool execution. The workflow test verified that a model confirmation flag cannot book a conversation appointment and a proposal cannot be confirmed from another session. Prompt injection resistance beyond booking is unverified. The direct booking API remains an unauthenticated operator route. |
| Medium | Partial CRM edits recomputed BANT using only request fields. Placeholder values received full points. | Score the merged record, reject common unknown markers, normalize updated contacts and return 409 for uniqueness conflicts. |
| Medium | Invalid timezones and reversed operating hours could be persisted. | Reject invalid settings with HTTP 422. |
| Medium | Empty uploads were reported as indexed. | Reject uploads without extractable text. Retrieval uses lexical TF-IDF. Neural semantic and multilingual retrieval remain open. |
| Medium | CSV exports passed spreadsheet formula prefixes through. | Prefix formula-like strings before export. |
| Medium | Health returned a static database-connected claim. Repeated end requests changed the recorded duration. | Health now executes a database query. Ending an ended conversation preserves its existing summary and timestamp. |
| Medium | Repeated Listen actions could start competing recognizers. Recognition could run during synthesis and survive navigation. | Added consent/state guards, recognizer cleanup and recoverable microphone errors. Physical microphone and synthesis remain unverified. |
| Medium | Booking rate divides all currently confirmed appointments by all conversations. Operator bookings can inflate the metric. | Open. Define and implement a session-attributed conversion rate. The dashboard otherwise reads actual database aggregates. |
| Medium | Cancelled starts remain reserved by the unconditional database uniqueness constraint. | Open. Needs an existing-database migration and concurrency tests. Rescheduling remains unavailable. |
| Medium | Session summaries can attribute another appointment on the same lead and list failed tool attempts as actions. | Open. Bind appointment attribution to the originating proposal and distinguish attempts from committed actions. |
| Medium | Lead identity rebinding, simultaneous API turns, tool action deduplication and cross-interval concurrent writes lack adequate coverage. | Open. The UI prevents overlapping submissions within its current component. That guard does not serialize backend requests. |
| Low | UI has incomplete CRM detail, microphone controls, and uneven error handling. Interview documentation overstates some memory and transaction guarantees. | Open. See the acceptance checklist and limitations. |

## Actual execution

| Command or check | Result |
|---|---|
| `.\.venv\Scripts\python -m pytest backend/tests -q` | 16 passed, 1 live test skipped, 1 upstream deprecation warning |
| `.\.venv\Scripts\python -m pip check` | No broken requirements |
| `npm run lint` in frontend | TypeScript passed |
| `npm run test` in frontend | 2 passed |
| `npm run build` in frontend | Passed. Vite warned about a 666.65 KB JavaScript bundle |
| `.\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --port 8023` and `npm run dev -- --host 127.0.0.1 --port 5183 --strictPort` with the proxy pointed at 8023 | Fresh app returned HTTP 200 for the frontend and proxied healthy database/config results. AI status reported false |
| `git diff --check` and Google API-key pattern scan in workspace sources | No diff whitespace errors or matching keys |

The automated journey covered TXT retrieval, CRM save, qualification, model confirmation rejection, cross-session proposal rejection, explicit proposal confirmation, repeated confirmation, summary and analytics. No random metric generation was found. The model error fallback is explicitly identified in code as an error response. There is no configured Playwright suite. Browser interaction, PDF lifecycle, Windows launcher supervision, database restart persistence and actual provider calls were not proven by the smoke checks.

## External checks

Configure a valid Gemini key for an account with access to the configured model. Set `SALESPILOT_LIVE_TEST=1` and run the provider test. Then run the demo script in Chromium with microphone permission and test both languages, denied permission, text fallback, and playback suppression. Confirm the stored records again after restarting. These checks are necessary before claiming the full live customer journey is assessment ready.
