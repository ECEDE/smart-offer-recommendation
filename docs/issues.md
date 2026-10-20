# GitHub Issues / acceptance criteria

Create these as public GitHub Issues and link each PR to its issue.

## Issue 1 — Repository and specification
- [ ] README describes problem, users, expected behavior and limitations.
- [ ] docs/spec.md documents primary journey and entities.
- [ ] AGENTS.md defines team responsibilities and process.
- [ ] Public issues have testable acceptance criteria.

## Issue 2 — Synthetic dataset and persistence
- [ ] Seed at least 30 synthetic customers and 12 distinct tariffs.
- [ ] PostgreSQL persists customers, runs, offers and acceptances.
- [ ] Rerunning the seed does not duplicate records.

## Issue 3 — Recommendation API
- [ ] Returns four unique ranked offers when >=4 eligible tariffs exist.
- [ ] Excludes tariffs outside GB or price rules.
- [ ] Returns a documented insufficient-offers response when <4 exist.
- [ ] Returns explanations and consistent ordering.
- [ ] Handles no eligible offers and invalid customer IDs.

## Issue 4 — Frontend customer journey
- [ ] Search and select customers.
- [ ] Show current tariff, usage and four ranked recommendations.
- [ ] Show why each offer was recommended.
- [ ] Show meaningful empty and error states.

## Issue 5 — Acceptance simulation and dashboard
- [ ] Persist exactly one acceptance per recommendation run.
- [ ] Display absolute and percentage uplift.
- [ ] Dashboard shows runs, acceptance rate and failures.
- [ ] Zero current price handled without division-by-zero.

## Issue 6 — Automated testing
- [ ] Unit tests cover boundary values, sorting and deduplication.
- [ ] Integration tests cover API + database + acceptance.
- [ ] Frontend test covers customer selection and recommendation display.
- [ ] Test commands are documented and pass in CI.

## Issue 7 — Docker and deployment
- [ ] `docker compose up --build` starts frontend, backend and database.
- [ ] Health checks and environment example provided.
- [ ] Public deployment or clear deployment demo evidence.

## Issue 8 — CI/CD and rollback
- [ ] Every pull request triggers automated tests.
- [ ] Merge triggers deployment to development.
- [ ] Production deployment is manually approved.
- [ ] Rollback procedure is documented and demonstrated.

## Issue 9 — Observability and alert
- [ ] A recommendation journey emits correlated traces, metrics and structured logs.
- [ ] Telemetry excludes sensitive customer data.
- [ ] A controlled recommendation failure raises a user-impact alert.
- [ ] Evidence shows the alert firing.

## Issue 10 — Incident responder agent
- [ ] Agent receives alert context and produces a diagnosis.
- [ ] Agent can execute only an allowlisted demo recovery action.
- [ ] Recovery is verified by a subsequent successful request.
- [ ] Every action and outcome is auditable.
