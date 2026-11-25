# Deployment

Local Windows setup uses `setup.ps1`; startup uses `start.ps1`. Configure `.env` from `.env.example`. SQLite is created in the working directory and the NovaCRM catalog is seeded idempotently.

Production should build immutable frontend/backend artifacts in CI, run tests and vulnerability scanning, host static output on S3/CloudFront, and deploy a container to ECS Fargate. Inject secrets from Secrets Manager, run schema migrations as a controlled job, perform health checks at `/api/health`, restrict allowed origins, enable TLS/WAF, and centralize logs without customer content. Back up and restore-test PostgreSQL before releases.
