# Security and Privacy

Optional Gemini embeddings send knowledge chunks and query text to Google. Enable this mode only for data approved for provider processing. The browser permission check and model access remain separate release gates.

The local MVP validates bodies with Pydantic, uses ORM-parameterized SQL, restricts CORS to `FRONTEND_ORIGIN`, validates file type/size, normalizes filenames, isolates messages by session ID, and never returns API keys. RAG content is marked untrusted. Tool names are allow-listed and arguments schema-validated; no arbitrary execution exists. Voice requires consent and raw audio is not retained.

This is an unauthenticated, single-business laptop demo. Production requires Cognito/OIDC authentication, role-based authorization, tenant IDs and row-level enforcement, TLS, KMS encryption, WAF/rate limiting, audit logs, redaction, retention/deletion workflows, DPA/consent governance, malware scanning, secret rotation, dependency scanning, and incident response. Real customer data should not be sent to Gemini without documented consent and policy review.
