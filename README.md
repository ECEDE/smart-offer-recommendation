# Smart Offer Recommendation

A full-stack telecom tariff recommendation and incident-response application built with synthetic customer data.

## Problem
Generic tariff offers may not fit customer usage or budget. This application recommends eligible mobile tariffs, records simulated acceptance, measures price uplift, and monitors failures affecting the recommendation journey.

## Users
- Customer service agent: browse customers, generate and accept offers.
- Operations engineer: monitor failures, review alerts and responder actions.

## MVP
1. Browse/search synthetic customer profiles (current GB, price, monthly usage).
2. Generate up to four unique, ranked, eligible offers from a tariff catalog.
3. Explain why each offer is eligible and how it ranks.
4. Simulate acceptance, persist the selection, and calculate absolute and percentage uplift.
5. Display recommendation counts, acceptance rates, and failed journeys.
6. Trigger an alert on a controlled recommendation failure and have a responder agent diagnose it and execute a safe, auditable recovery action.

## Business rules (initial proposal)
- Candidate GB >= max(0, current plan GB - 5).
- Candidate GB <= observed usage GB + 10.
- Candidate price > current plan price.
- Deduplicate tariff IDs; rank by lower eligible GB first, then deterministic score.
- Return four offers if at least four eligible tariffs exist. Otherwise return available eligible offers and a structured insufficiency reason; do not silently break eligibility rules.
- Price uplift = accepted offer price - current plan price; percentage uplift = 100 * uplift / current plan price (undefined if current price is zero).

## Stack
React + TypeScript frontend; FastAPI + Python backend; PostgreSQL database; Docker Compose; pytest + frontend tests; GitHub Actions; OpenTelemetry; alerting and a guarded responder agent.

## Local run
To be documented once the implementation is ready. Target: `docker compose up --build`.

## Safety and privacy
Use only synthetic customer records. No real MSISDNs, subscription IDs, personal data, secrets, or internal production data in the public repository.

## Project documentation
- [Product specification](docs/spec.md)
- [Agent team and context](AGENTS.md)
- [Acceptance criteria and issue plan](docs/issues.md)

## Step 2 backend scaffold
See [backend setup](backend/README.md). This is a local API milestone, not the complete full-stack product.
