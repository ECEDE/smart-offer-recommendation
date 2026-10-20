# Docker Compose — Smart Offer Recommendation

This package is an **overlay**: copy its files into the existing repository, keeping the existing backend code, frontend source, and frontend `package-lock.json`.

## Prerequisites

- Docker Desktop installed and running.
- Existing project includes `backend/app/main.py`, `backend/upgrade_tariffs.py`, `backend/requirements.txt`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/src`, and `frontend/index.html`.
- Frontend requests use relative `/api` paths (as in the dashboard package).

## Install

From the existing project root:

```bash
cp -R ~/Downloads/smart-offer-docker/. .
docker compose up --build -d
```

Open http://localhost:8080 and test Customer 15 recommendations and acceptance. Backend API is proxied at http://localhost:8080/api/health.

## Verify

```bash
docker compose ps
docker compose logs --tail=60 backend
docker compose logs --tail=60 frontend
curl http://localhost:8080/api/health
```

## Stop

```bash
docker compose down
```

**Do not use `docker compose down -v`** unless you deliberately want to delete the Docker-managed SQLite database. The Docker database is separate from your local `backend/smart_offers.db`; local historical runs are not migrated automatically.

The backend startup script seeds and upgrades synthetic tariffs idempotently. Frontend Nginx proxies `/api/` to the backend service. This is a local containerized deployment, not yet a public production deployment or CI/CD.
