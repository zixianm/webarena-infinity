import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    if not emails:
        return False, "No emails found in state."

    # CloudScale-related email IDs that should have the Legal label
    cloudscale_ids = {13, 21, 43, 101}
    legal_label = "label_9"

    email_map = {e.get("id"): e for e in emails}

    failures = []
    for eid in cloudscale_ids:
        email = email_map.get(eid)
        if email is None:
            failures.append(f"Email id={eid} not found in state")
            continue

        labels = email.get("labels", [])
        if legal_label not in labels:
            subject = email.get("subject", "unknown")
            failures.append(
                f"Email id={eid} ('{subject}') missing '{legal_label}' (Legal). "
                f"Current labels: {labels}"
            )

    if failures:
        return False, "Not all CloudScale emails have the Legal label: " + "; ".join(failures)

    return True, (
        "All CloudScale-related emails (ids 13, 21, 43, 101) have the 'Legal' label (label_9)."
    )
