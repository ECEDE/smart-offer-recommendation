# Synthetic tariff catalog fix

This upgrade fixes `insufficient_offers` caused by the original sparse synthetic catalog. It adds four distinct higher-price tariffs for each existing customer profile while respecting the original GB eligibility window. It does not delete customers, previous recommendation runs, or acceptances.

From the `backend` directory, stop the API and run:

```bash
cp smart_offers.db smart_offers.db.backup  # if the DB exists
python upgrade_tariffs.py
pytest -q
uvicorn app.main:app --reload
```

Then test `POST /customers/2/recommendations` and `POST /customers/11/recommendations` in `/docs`. The upgrade is safe to rerun: existing synthetic IDs are not overwritten.

**Scope:** Demo seed data only. The upgrade uses deterministic price variants, not ML predictions or real-world pricing. Future ranking work should distinguish tariff price variants from genuinely different commercial products.
