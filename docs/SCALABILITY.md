# Scalability Strategy: 100,000 Registered Users

Assume 100,000 registered users, 20,000 daily active users, a 10% peak-hour share, and 5% of peak users in simultaneous voice sessions: about 100 concurrent sessions. At six turns per five-minute session, peak generation is roughly 120 requests/minute; quotas and latency must be measured rather than assumed.

Host the Vite bundle on S3 behind CloudFront. Route API traffic through WAF and an Application Load Balancer to stateless ECS Fargate tasks. Cognito issues tenant-scoped identity. Store transactional data in Multi-AZ RDS PostgreSQL with PgBouncer-style pooling, composite tenant/time indexes, read replicas for analytics, and point-in-time recovery. Use a managed vector service or PostgreSQL pgvector for embeddings. ElastiCache Redis holds rate limits, ephemeral session summaries, and hot catalog results. SQS absorbs summaries, ingestion, CRM sync, and analytics jobs with dead-letter queues and backpressure.

Autoscale Fargate on request count, CPU, latency, and queue depth. If one task safely handles 40 concurrent API requests, four tasks provide 160-request capacity plus headroom; confirm through load tests. Cache identical product retrievals, bound history/tool loops, batch embeddings, enforce tenant quotas, and use provider-aware circuit breakers. Secrets Manager stores credentials; CloudWatch collects structured logs, metrics, traces, alarms, and cost signals.

Partition every record by tenant, enforce authorization in service and database layers, and encrypt with tenant-aware keys where required. Multi-AZ services cover normal failure; cross-region backups and a documented restore drill target explicit RPO/RTO. This is a proposed architecture—the local SQLite MVP has not been load-tested for 100,000 users.
