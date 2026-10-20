# Backend — local run

Requires Python 3.10+.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to try the API.

Tests (in the backend directory):

```bash
pytest -q
```

The initial milestone uses SQLite; the planned PostgreSQL migration and React frontend are **not yet implemented**.
