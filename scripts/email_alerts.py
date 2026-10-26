import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

STATE_FILE = Path("/tmp/smart_offer_alert_state.json")
API_URL = os.getenv("MONITORING_URL", "http://127.0.0.1:8000/agent/investigate")
EMAIL = os.environ["SMART_OFFER_ALERT_EMAIL"]
REGION = "eu-central-1"


def send_email(subject, body):
    subprocess.run(
        [
            "aws", "ses", "send-email",
            "--from", EMAIL,
            "--destination", f"ToAddresses={EMAIL}",
            "--message", json.dumps({
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
            }),
            "--region", REGION,
        ],
        check=True,
    )


def get_monitoring():
    try:
        with urllib.request.urlopen(API_URL, timeout=10) as response:
            data = json.load(response)

        monitoring = data["monitoring"]
        if monitoring["alert"]:
            return "ALERT", json.dumps(data, indent=2, ensure_ascii=False)

        return "OK", "Monitoring metrics are back to normal."

    except Exception as exc:
        return "DOWN", f"Backend monitoring endpoint is unreachable: {exc}"


def main():
    status, details = get_monitoring()

    previous = "OK"
    if STATE_FILE.exists():
        previous = json.loads(STATE_FILE.read_text()).get("status", "OK")

    if status != previous:
        if status == "OK":
            send_email(
                "RECOVERY - Smart Offer Monitoring",
                f"Previous status: {previous}\nCurrent status: OK\n\n{details}",
            )
        else:
            send_email(
                f"ALERT - Smart Offer Monitoring - {status}",
                details,
            )

        STATE_FILE.write_text(json.dumps({"status": status}))

    print(f"Monitoring status: {status}, previous: {previous}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Monitoring notification failed: {exc}", file=sys.stderr)
        sys.exit(1)
