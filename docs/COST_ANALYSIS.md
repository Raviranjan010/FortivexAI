# Commercial Feasibility and Illustrative Costs

If semantic retrieval is enabled, include document embedding on cache misses and one query embedding per semantic search. Tool follow-up rounds and optional end-of-call excerpt selection also add generation requests.

Target customers are small and mid-market B2B teams with repetitive inbound enquiries. Value comes from faster response, consistent qualification, fewer manual updates, and more bookable coverage—not guaranteed revenue.

Possible pricing combines a base subscription (workspace, seats, CRM, analytics) with usage for AI turns or voice minutes. A prototype uses a laptop and free/low-volume provider tiers. A small-business deployment adds CloudFront/S3, two API tasks, a small managed database, monitoring, and AI usage. A scaled deployment adds Multi-AZ PostgreSQL, Redis, queues, more tasks, vector retrieval, backups, and support.

Use current vendor calculators before purchase. Illustrative monthly formula: `infrastructure + database + storage + monitoring + (AI input tokens × input rate) + (AI output tokens × output rate) + (voice minutes × voice rate) + support`. If a plan charges ₹30,000 and variable delivery costs are ₹8,000, contribution margin is `(30,000-8,000)/30,000 = 73%` before acquisition, payroll, tax, and support. These figures are scenarios, not verified vendor prices or revenue forecasts. Customer acquisition, onboarding, churn, provider quota commitments, compliance, and human escalation materially affect margin.
