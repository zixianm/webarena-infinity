import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    if not emails:
        return False, "No emails found in state."

    # Calendar invite emails that were in inbox
    calendar_invite_ids = {44, 45, 46, 47, 48, 49, 118}

    email_map = {e.get("id"): e for e in emails}

    failures = []
    for eid in calendar_invite_ids:
        email = email_map.get(eid)
        if email is None:
            failures.append(f"Email id={eid} not found in state")
            continue

        if not email.get("isDone", False):
            subject = email.get("subject", "unknown")
            failures.append(
                f"Email id={eid} ('{subject}') is not marked as done. isDone={email.get('isDone')}"
            )

    if failures:
        return False, (
            f"{len(failures)} calendar invite email(s) not marked as done: " + "; ".join(failures)
        )

    return True, "All calendar invite emails (ids 44, 45, 46, 47, 48, 49, 118) are marked as done."
