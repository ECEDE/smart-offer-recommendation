"""Initial FastAPI scaffold using synthetic records and SQLite.
PostgreSQL, React, observability and agent responder are later milestones.
"""
import os
import json
import logging
import time
from datetime import datetime, timezone
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .oncall_agent import analyze_alert

DB_PATH = os.environ.get("SMART_OFFER_DB", str(Path(__file__).resolve().parents[1] / "smart_offers.db"))
app = FastAPI(title="Smart Offer Recommendation", version="0.2.0")

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("smart_offer")

def log_event(event_type, **fields):
    logger.info(json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **fields
    }))


@contextmanager
def db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()

def initialize():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, current_gb REAL NOT NULL, current_price REAL NOT NULL, usage_gb REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS tariffs (id INTEGER PRIMARY KEY, name TEXT NOT NULL, gb REAL NOT NULL, price REAL NOT NULL, active INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, customer_id INTEGER NOT NULL, status TEXT NOT NULL, reason TEXT);
        CREATE TABLE IF NOT EXISTS offers (run_id TEXT NOT NULL, tariff_id INTEGER NOT NULL, rank INTEGER NOT NULL, PRIMARY KEY(run_id, tariff_id));
        CREATE TABLE IF NOT EXISTS acceptances (run_id TEXT PRIMARY KEY, tariff_id INTEGER NOT NULL, before_price REAL NOT NULL, accepted_price REAL NOT NULL);
        """)
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(runs)")
        }
        if "created_at" not in columns:
            conn.execute("ALTER TABLE runs ADD COLUMN created_at TEXT")
        conn.executemany("INSERT OR IGNORE INTO customers VALUES (?, ?, ?, ?)", [(i, float([10,20,30,40][i%4]), float(200+(i%4)*100), float([12,18,24,33][i%4])) for i in range(1,31)])
        conn.executemany("INSERT OR IGNORE INTO tariffs VALUES (?, ?, ?, ?, 1)", [(i,f"Plan {i}",float(5+i*5),float(150+i*45)) for i in range(1,17)])

@app.on_event("startup")
def on_startup():
    initialize()

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/customers")
def customers():
    with db() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM customers ORDER BY id")]

@app.get("/customers/{customer_id}")
def customer(customer_id: int):
    with db() as conn:
        row=conn.execute("SELECT * FROM customers WHERE id=?",(customer_id,)).fetchone()
        if row is None: raise HTTPException(404,"Customer not found")
        return dict(row)

def eligible_tariffs(customer, tariffs):
    low=max(0, customer["current_gb"]-5)
    high=customer["usage_gb"]+10
    return sorted((t for t in tariffs if t["active"] and low<=t["gb"]<=high and t["price"]>customer["current_price"]),key=lambda t:(t["gb"],t["price"],t["id"]))[:4]

@app.post("/customers/{customer_id}/recommendations")
def recommend(customer_id: int):
    start = time.perf_counter()
    with db() as conn:
        c=conn.execute("SELECT * FROM customers WHERE id=?",(customer_id,)).fetchone()
        if c is None: raise HTTPException(404,"Customer not found")
        tariffs=[dict(r) for r in conn.execute("SELECT * FROM tariffs")]
        selected=eligible_tariffs(dict(c),tariffs)
        run_id=str(uuid4())
        status="success" if len(selected)==4 else "insufficient_offers"
        reason=None if status=="success" else f"Only {len(selected)} eligible offers found; 4 required"
        conn.execute(
            "INSERT INTO runs (id, customer_id, status, reason, created_at) VALUES (?, ?, ?, ?, ?)",
            (run_id, customer_id, status, reason, datetime.now(timezone.utc).isoformat())
        )
        conn.executemany("INSERT INTO offers VALUES (?, ?, ?)",[(run_id,t["id"],i) for i,t in enumerate(selected,1)])
        log_event(
            "recommendation",
            customer_id=customer_id,
            run_id=run_id,
            status=status,
            offer_count=len(selected),
            duration_ms=round((time.perf_counter()-start)*1000, 2)
        )
        return {"run_id":run_id,"status":status,"reason":reason,"offers":[{"rank":i,"tariff_id":t["id"],"name":t["name"],"gb":t["gb"],"price":t["price"],"explanation":"Eligible by GB and price; ranked by ascending GB, price and ID"} for i,t in enumerate(selected,1)]}

class Acceptance(BaseModel):
    tariff_id: int

@app.post("/recommendation-runs/{run_id}/acceptances")
def accept(run_id: str, payload: Acceptance):
    with db() as conn:
        row=conn.execute("SELECT c.current_price, t.price FROM runs r JOIN customers c ON c.id=r.customer_id JOIN offers o ON o.run_id=r.id JOIN tariffs t ON t.id=o.tariff_id WHERE r.id=? AND o.tariff_id=?",(run_id,payload.tariff_id)).fetchone()
        if row is None: raise HTTPException(404,"Run or recommended tariff not found")
        if conn.execute("SELECT 1 FROM acceptances WHERE run_id=?",(run_id,)).fetchone(): raise HTTPException(409,"This run already has an acceptance")
        before,after=row["current_price"],row["price"]
        conn.execute("INSERT INTO acceptances VALUES (?, ?, ?, ?)",(run_id,payload.tariff_id,before,after))
        log_event(
            "acceptance",
            run_id=run_id,
            tariff_id=payload.tariff_id,
            status="success",
            uplift=round(after-before, 2)
        )
        return {"run_id":run_id,"tariff_id":payload.tariff_id,"uplift":round(after-before,2),"uplift_pct":round(100*(after-before)/before,2) if before else None}

@app.get("/dashboard/metrics")
def metrics():
    with db() as conn:
        runs=conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        accepted=conn.execute("SELECT COUNT(*) FROM acceptances").fetchone()[0]
        failures=conn.execute("SELECT COUNT(*) FROM runs WHERE status!='success'").fetchone()[0]
        return {"recommendation_runs":runs,"acceptances":accepted,"acceptance_rate_pct":round(100*accepted/runs,2) if runs else 0,"insufficient_offer_runs":failures}


@app.get("/monitoring/alerts")
def monitoring_alerts():
    """Evaluate recommendation failures over the last 15 minutes."""
    from datetime import timedelta

    window_start = (
        datetime.now(timezone.utc) - timedelta(minutes=15)
    ).isoformat()

    with db() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_runs,
                SUM(CASE WHEN status != 'success' THEN 1 ELSE 0 END) AS failed_runs
            FROM runs
            WHERE created_at >= ?
            """,
            (window_start,)
        ).fetchone()

    total = row["total_runs"] or 0
    failed = row["failed_runs"] or 0
    failure_rate = round(100 * failed / total, 2) if total else 0

    alert = total > 0 and failure_rate > 10

    return {
        "window_minutes": 15,
        "total_runs": total,
        "failed_runs": failed,
        "failure_rate_pct": failure_rate,
        "threshold_pct": 10,
        "alert": alert,
        "severity": "critical" if alert else "ok",
        "message": (
            "High recommendation failure rate detected"
            if alert
            else "Recommendation failure rate within threshold"
        )
    }



@app.get("/agent/investigate")
def investigate():
    """Investigate current recommendation monitoring alerts."""
    alert_data = monitoring_alerts()
    analysis = analyze_alert(alert_data)

    return {
        "monitoring": alert_data,
        "investigation": analysis,
    }
