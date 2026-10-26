---
name: smart-offer-investigator
description: Investigate Smart Offer Recommendation incidents, monitoring alerts, and failed recommendation runs.
---

# Smart Offer Incident Investigator

## Purpose

Help AI coding agents investigate production issues in the Smart Offer Recommendation application.

## When to use

Use this skill when:
- Recommendation failure rate exceeds 10%.
- The backend monitoring endpoint is unavailable.
- Customers receive insufficient tariff recommendations.
- An investigation of failed recommendation runs is requested.

## Investigation workflow

1. Read `AGENTS.md` and `docs/spec.md`.
2. Check the monitoring endpoint: `GET /monitoring/alerts`.
3. Retrieve investigation results: `GET /agent/investigate`.
4. Examine recent failed recommendation runs.
5. Identify whether failures are caused by:
   - GB eligibility constraints
   - Price eligibility constraints
   - Missing customer data
   - Insufficient eligible tariff candidates
   - Backend or database errors
6. Review structured application logs.
7. Summarize findings and recommend corrective actions.

## Expected output

Provide:
- Incident severity
- Current monitoring status
- Affected customer count, if available
- Likely root causes
- Supporting evidence
- Recommended next actions

## Safety rules

- Never expose customer identifiers or credentials in public reports.
- Never modify production data without explicit approval.
- Never restart production services automatically.
- Never disable monitoring or security checks to hide failures.
- Treat recommendations as hypotheses until validated.


## Useful commands

Run from the project directory:

- Check containers: `sudo docker compose ps`
- Check backend logs: `sudo docker compose logs backend --tail=100`
- Investigate incidents: `GET /agent/investigate`
