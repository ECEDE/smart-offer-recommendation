"""Add synthetic tariffs without deleting existing customers or historical runs.
Run from backend directory: python upgrade_tariffs.py
"""
from app.main import initialize, db, eligible_tariffs

initialize()
with db() as conn:
    customers = [dict(r) for r in conn.execute('SELECT * FROM customers ORDER BY id')]
    profiles = sorted({(c['current_gb'], c['current_price'], c['usage_gb']) for c in customers})
    added = 0
    for index, (current_gb, current_price, usage_gb) in enumerate(profiles):
        low = max(0, current_gb - 5)
        high = usage_gb + 10
        if low > high:
            print(f'WARNING: impossible GB window for profile {index}: {low} > {high}')
            continue
        # Four price alternatives for the same eligible GB; each has a distinct tariff ID.
        gb = round(max(low, min(current_gb, high)), 2)
        for j in range(4):
            tariff_id = 10001 + index * 4 + j
            price = round(current_price + 30 * (j + 1), 2)
            # INSERT OR IGNORE preserves a previously edited record with the same ID.
            result = conn.execute(
                'INSERT OR IGNORE INTO tariffs (id, name, gb, price, active) VALUES (?, ?, ?, ?, 1)',
                (tariff_id, f'Synthetic {gb:g} GB Plus {j+1}', gb, price),
            )
            added += result.rowcount
    tariffs = [dict(r) for r in conn.execute('SELECT * FROM tariffs')]
    failures = [(c['id'], len(eligible_tariffs(c, tariffs))) for c in customers if len(eligible_tariffs(c, tariffs)) < 4]
    print(f'Customers: {len(customers)} | Added tariffs: {added} | Total tariffs: {len(tariffs)}')
    print(f'Customers with fewer than 4 eligible offers: {len(failures)}')
    if failures:
        print('Failures:', failures)
        raise SystemExit(1)
    print('SUCCESS: all existing customers have at least 4 eligible offers.')
