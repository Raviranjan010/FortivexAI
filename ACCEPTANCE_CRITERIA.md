# Acceptance Criteria

- [x] Health and safe configuration endpoints work without exposing secrets.
- [x] Persistent isolated sessions retain bounded conversational context.
- [ ] Gemini adapter returns validated responses and surfaces provider failures. Local timeout test passes. Live verification is pending.
- [ ] Voice UI implements IDLE/LISTENING/PROCESSING/SPEAKING/ERROR/ENDED plus text fallback. Browser verification and microphone activity features are pending.
- [x] TXT/PDF documents are validated, chunked, indexed, retrieved with sources, and fully deleted.
- [x] Validated bounded tools execute real services and log observable outcomes.
- [x] BANT scoring is deterministic and evidence-based; sentiment is transcript-only.
- [ ] CRM provides dedicated customer detail views and UI search/filter controls. Basic lead operations and CSV export exist.
- [x] Booking rejects past/out-of-hours/conflicting/unconfirmed requests and persists confirmed ones.
- [x] Summary business facts and booking conversion use session-attributed database records. An optional Gemini purpose excerpt must match the customer transcript.
- [ ] Live neural retrieval quality in English and Hindi has been verified with the configured account.
- [ ] Nine pages exist. Browser accessibility and consistent error states remain to be verified.
- [x] Backend suite, frontend tests, typecheck, and production build pass.
- [x] Required operational, security, architecture, cost, and interview documentation exists.
- [x] Live Gemini and microphone checks are explicitly reported as unverified.
