import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    pagerduty_emails = [
        email for email in emails
        if email.get("from", {}).get("email") == "alerts@pagerduty.com"
    ]

    if len(pagerduty_emails) == 0:
        return False, "No emails from alerts@pagerduty.com found in state."

    failures = []
    for email in pagerduty_emails:
        if not email.get("isTrashed", False):
            failures.append(
                f"Email '{email.get('subject')}' (id {email.get('id')}) from PagerDuty "
                f"should be trashed (isTrashed=True) but isTrashed={email.get('isTrashed')}."
            )

    if failures:
        return False, " ".join(failures)

    return True, f"All {len(pagerduty_emails)} PagerDuty alert emails have been moved to trash."
