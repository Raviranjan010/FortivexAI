# Assessment release coverage

Live recheck on 2026-11-26: the workspace contained only `.env.example`. No Gemini key was visible to the process, user, or machine environment. The real provider test skipped. The application started on backend 8030 and frontend 5190. Live account/model access and the real AI business workflow remain unverified.

Final rehearsal check, 2026-11-26: the updated Windows launcher passed on backend 8030 and frontend 5190. Port 8011 was occupied. Neither the local `.env` file nor the environment key was present. The opt-in live test skipped, so the live customer journey and embedding account access remain open. The browser host was unavailable, leaving page inspection, microphone, and print preview open. The report contains about 393 words and the architecture SVG parses with a 1200×520 viewBox.

| Requirement | Implementation and verification |
|---|---|
| Windows startup | Verified launcher readiness and proxied database health on ports 5186 and 8026. |
| Gemini generation | Official SDK, structured generation, sanitized errors. Live account/model verification blocked by missing credentials. |
| Agent execution | Validated structured JSON requests, four execution rounds and identical-call suppression within a turn. Native Gemini function calling remains future scope. |
| Knowledge retrieval | Optional Gemini embeddings with persistent chunk vectors and a cosine threshold. English paraphrase and Hindi tested with deterministic embeddings. Labelled TF-IDF fallback. |
| Lead and sentiment | Four deterministic BANT evidence levels. Gemini classifies transcript sentiment when available. A lexical fallback is labelled. |
| Scheduling and CRM | Session-bound confirmation and proposal idempotency. SQLite migration, cancelled slot reuse and competing interval writes tested. Rescheduling remains open. |
| Summary and analytics | A validated transcript quote is optional. Business actions and appointment attribution come from persisted records. Booking rate counts distinct sessions with a confirmed proposal divided by all sessions. |
| Frontend voice | Consent, speech fallback and input meter implemented. Physical microphone and English/Hindi recognition need a browser rehearsal. |
| Browser and submission | API journey, frontend unit tests and production build passed. Playwright and a printed report check remain open. |
