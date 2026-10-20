# Product specification (v0.1)

## Primary journey
1. Agent opens the customer list.
2. Agent selects a synthetic customer and views current tariff, price, and usage.
3. Agent requests recommendations.
4. API applies eligibility rules, deduplicates, ranks, and returns up to four offers with explanations.
5. Agent accepts one offer. The API stores the acceptance and computes uplift.
6. Dashboard shows aggregate recommendation and acceptance metrics.

## Data entities
- Customer(id, current_tariff_id, current_gb, current_price, usage_gb)
- Tariff(id, name, gb, price, active)
- RecommendationRun(id, customer_id, status, created_at, failure_reason, trace_id)
- RecommendedOffer(id, run_id, tariff_id, rank, score, explanation)
- Acceptance(id, run_id, tariff_id, accepted_at, before_price, accepted_price)
- Incident(id, type, status, trace_id, created_at, diagnosis, recovery_action)

## API outline
- GET /health
- GET /customers?search=
- GET /customers/{id}
- POST /customers/{id}/recommendations
- POST /recommendation-runs/{run_id}/acceptances
- GET /dashboard/metrics
- GET /incidents
- POST /demo/trigger-failure (demo-only, access controlled)

## Nonfunctional expectations
- Local full-stack start with one Docker Compose command.
- Reproducible synthetic seed data.
- Unit, integration, and frontend tests; one-command test instructions.
- Request correlation IDs, structured logs, latency/error metrics, and traces.
- No customer identifiers or secrets in telemetry.
- Agent recovery restricted to an allowlist, recorded in an audit trail; no unreviewed production changes.

## Out of scope for MVP
- Production telecom integration, live customer data, billing, payments, and automatic production tariff changes.
- Full ML training pipeline (optional stretch goal).

## Definition of done
- All MVP acceptance criteria in docs/issues.md pass.
- CI is green; application deployed to a demonstrable URL.
- Alert and responder demonstration is reproducible.
- Public issue tracker and documentation show development evidence.
