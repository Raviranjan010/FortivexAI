# Interview Preparation

## Code map

- `backend/app/main.py`: HTTP routes and bounded chat orchestration.
- `backend/app/ai.py`: official Gemini client and structured response contract.
- `backend/app/tools.py`: ten allow-listed tools, schemas, logging.
- `backend/app/services.py`: retrieval, BANT, sentiment, CRM, booking, analytics.
- `backend/app/models.py`: normalized persistent entities and constraints.
- `frontend/src/main.tsx`: pages and browser speech workflow.
- `frontend/src/voice.ts`: explicit transition rules.

## Questions and concise answers

- **Generative vs agentic AI?** Generative AI writes a response; agentic orchestration selects validated tools and incorporates their observable outcomes.
- **RAG/embeddings/similarity?** Documents are chunked, represented as TF-IDF character n-gram vectors, and ranked by cosine similarity. Production can swap in neural embeddings without changing route contracts.
- **Function calling?** Gemini returns schema-validated tool requests; the allow-list validates arguments, caps calls at three, executes services, records events, and gives outcomes back to the model.
- **Memory?** Messages belong to a UUID session. Only the last 12 turns enter the bounded prompt; persisted summaries represent older context.
- **Speech?** Chromium recognition converts microphone speech to text; synthesis reads the reply. Recognition stops during synthesis to avoid feedback; text is the fallback.
- **Lead scoring?** `bant()` awards 25 each for evidenced budget, authority, need, and timeline. Unknown is zero; thresholds are Hot 75+, Warm 40+, Cold below 40.
- **Sentiment?** The MVP classifies transcript words, not voice emotion or biometrics.
- **Transactions/double booking?** `services.book()` checks confirmation/time/business rules; a unique start constraint and commit catch prevent races.
- **Security/prompt injection?** Pydantic, ORM queries, CORS, upload limits, secret isolation, untrusted-context instructions, and tool allow-listing reduce risk; production still needs identity and tenant isolation.
- **AWS scale/cost?** CloudFront/S3, ALB/Fargate, RDS, Redis, SQS, Cognito, Secrets Manager, CloudWatch. Scale on measured concurrency and compute unit economics from infrastructure plus provider usage.
- **Trade-off?** Local TF-IDF/SQLite makes the interview demo reliable and understandable; managed vector search/PostgreSQL are production upgrades.
