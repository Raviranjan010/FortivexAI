# Architecture

```mermaid
flowchart LR
  C[Customer] -->|consent + speech| B[React browser UI]
  B --> STT[Browser STT]
  STT --> API[FastAPI boundary]
  API --> A[Agent orchestrator]
  A --> G[Gemini API]
  A --> R[Optional Gemini embeddings or TF-IDF fallback]
  A --> T[Validated business tools]
  R --> DB[(SQLite: chunks and cached vectors)]
  T --> CRM[(SQLite: CRM/appointments)]
  API --> M[(Conversation memory)]
  CRM --> BI[Analytics queries]
  G --> API --> B --> TTS[Browser TTS] --> C
```

The browser is the microphone/audio security boundary; raw audio is not uploaded or retained. CORS restricts the local API origin. FastAPI/Pydantic validate ingress, SQLAlchemy parameterizes storage, and the Gemini adapter receives bounded history plus retrieved context. Retrieved text is explicitly treated as data rather than instructions. SQLite supports the laptop demonstration; production replaces it with PostgreSQL and a managed vector store.
