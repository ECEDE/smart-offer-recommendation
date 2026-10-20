"""Check monitoring alerts and run the on-call investigation."""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

API_URL = os.getenv(
    "SMART_OFFER_API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


def main():
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        with urllib.request.urlopen(
            f"{API_URL}/agent/investigate",
            timeout=10
        ) as response:
            data = json.load(response)

    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        print(json.dumps({
            "timestamp": timestamp,
            "event_type": "monitoring_check_failed",
            "error": str(exc),
        }))
        return 2

    monitoring = data["monitoring"]
    investigation = data["investigation"]

    result = {
        "timestamp": timestamp,
        "event_type": "monitoring_check",
        "alert": monitoring["alert"],
        "failure_rate_pct": monitoring["failure_rate_pct"],
        "total_runs": monitoring["total_runs"],
        "failed_runs": monitoring["failed_runs"],
        "severity": investigation["severity"],
        "summary": investigation["summary"],
        "failed_runs_analysis": data.get("failed_runs_analysis", []),
    }

    print(json.dumps(result, ensure_ascii=False))

    return 1 if monitoring["alert"] else 0


if __name__ == "__main__":
    sys.exit(main())
