# Agent team and working agreement

## Roles
- Product/spec agent: owns requirements, acceptance criteria, issue tracking.
- Backend agent: API, recommendation rules, persistence.
- Frontend agent: customer journey and dashboard.
- QA agent: tests, edge cases, regression checks.
- DevOps/observability agent: Docker, CI/CD, telemetry, alerts.
- Incident responder agent: triage alerts, inspect safe telemetry, run allowlisted recovery, audit results.

## Process
1. Read README.md and docs/spec.md before changing code.
2. Select a GitHub Issue with explicit acceptance criteria.
3. Make small, reviewable changes tied to the issue.
4. Run relevant tests and update documentation.
5. Open a pull request; verify CI and acceptance evidence.
6. Never commit secrets or real customer data.

## Agent constraints
The responder must not modify tariff prices, customer acceptances, production infrastructure, or secrets. Initial permitted recovery: enable a prevalidated rule-based recommendation fallback in the demo environment, with audit logging and idempotency.

## References
- docs/spec.md
- docs/issues.md
