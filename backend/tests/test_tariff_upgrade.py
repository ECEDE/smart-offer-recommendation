import os
import subprocess
import sys
from pathlib import Path

def test_tariff_upgrade_is_idempotent(tmp_path):
    backend = Path(__file__).resolve().parents[1]
    env = {**os.environ, 'SMART_OFFER_DB': str(tmp_path / 'upgrade.db')}
    command = [sys.executable, str(backend / 'upgrade_tariffs.py')]
    first = subprocess.run(command, cwd=backend, env=env, capture_output=True, text=True)
    assert first.returncode == 0, first.stdout + first.stderr
    assert 'Customers with fewer than 4 eligible offers: 0' in first.stdout
    second = subprocess.run(command, cwd=backend, env=env, capture_output=True, text=True)
    assert second.returncode == 0, second.stdout + second.stderr
    assert 'Added tariffs: 0' in second.stdout
