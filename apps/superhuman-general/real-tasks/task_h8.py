import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    blocked_senders = settings.get("blockedSenders", [])

    if not isinstance(blocked_senders, list):
        return False, f"Expected 'blockedSenders' to be a list, got {type(blocked_senders).__name__}."

    # Normalize to lowercase for comparison
    blocked_lower = [s.lower() if isinstance(s, str) else s for s in blocked_senders]

    failures = []
    expected_blocked = {
        "alerts@pagerduty.com": "PagerDuty",
        "alerts@datadog.com": "Datadog",
    }

    for email_addr, service_name in expected_blocked.items():
        if email_addr.lower() not in blocked_lower:
            failures.append(
                f"'{email_addr}' ({service_name}) is not in blockedSenders. "
                f"Current blocked senders: {blocked_senders}."
            )

    if failures:
        return False, " ".join(failures)

    return True, "Both PagerDuty and Datadog alert addresses are in blockedSenders."
