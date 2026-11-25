# Five-Minute Demo

Start with `powershell -ExecutionPolicy Bypass -File .\start.ps1 -BackendPort 8011`. Before the assessment, verify the configured Gemini model with the opt-in live test and rehearse microphone permission, playback and text fallback in Chromium.

1. Run setup/start, open the Overview, and note database-derived zero/actual values.
2. Open Knowledge Base and show the seeded NovaCRM catalog; upload a small TXT policy if desired.
3. Open Live Agent, select English/Hindi, accept consent, and start. Ask “What is the Growth plan price?” Use text if STT is unavailable.
4. Provide fictional name/email, company size, need, approved budget, decision authority, and timeline. Explain that BANT is deterministic.
5. Request a demo. Review the slot in Agent activity and click **Confirm appointment**. The confirmation status comes from the booking API.
6. End the call; show persisted summary/history, CRM lead, appointment, tool activity in the response, and updated analytics.
7. Restart and show persistence. Clearly state whether Gemini/microphone were live-verified.
