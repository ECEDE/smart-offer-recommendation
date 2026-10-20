"""On-call alert analysis for Smart Offer Recommendation."""


def analyze_alert(alert_data: dict) -> dict:
    """Analyze monitoring results and recommend corrective actions."""

    total = alert_data.get("total_runs", 0)
    failed = alert_data.get("failed_runs", 0)
    rate = alert_data.get("failure_rate_pct", 0)
    alert = alert_data.get("alert", False)

    if not alert:
        return {
            "status": "healthy",
            "severity": "ok",
            "summary": "Recommendation system is operating normally.",
            "recommended_actions": [],
        }

    return {
        "status": "investigation_required",
        "severity": "critical",
        "summary": (
            f"Recommendation failure rate is {rate}% "
            f"({failed}/{total} runs), exceeding the 10% threshold."
        ),
        "possible_causes": [
            "Insufficient eligible tariffs",
            "Restrictive GB eligibility boundaries",
            "Tariff price eligibility constraints",
            "Inactive or unavailable tariffs",
        ],
        "recommended_actions": [
            "Inspect failed recommendation runs.",
            "Review customer GB usage and current tariff.",
            "Verify active tariff availability.",
            "Check recommendation eligibility rules.",
        ],
    }
