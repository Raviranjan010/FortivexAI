# Known Limitations

- Live Gemini behavior requires a valid `GEMINI_API_KEY` and is not represented by deterministic automated provider tests.
- Browser Speech Recognition support varies; Chromium is recommended and text input remains available.
- The MVP analyzes transcript sentiment, not vocal emotion or biometric signals.
- Local deployment is unauthenticated and single-business; it is not production multi-tenant SaaS.
- Local TF-IDF retrieval is appropriate for the demo corpus, not a large production knowledge estate.
- External Salesforce/HubSpot and Google/Outlook calendar integrations are adapter extension points, not implemented connections.
