import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])
    user_email = state.get("currentUser", {}).get("email", "alex.morgan@acmecorp.com")

    # IDs of Important split inbox emails with attachments (excluding sent)
    target_ids = {1, 5, 9, 10, 18, 22, 120}

    email_map = {e.get("id"): e for e in emails}
    failures = []

    for eid in target_ids:
        e = email_map.get(eid)
        if e is None:
            failures.append(f"Email id={eid} not found")
            continue
        if not e.get("remindAt"):
            failures.append(f"Email id={eid} '{e.get('subject','')}' has no reminder set")

    if failures:
        return False, f"{len(failures)} email(s) missing reminders: " + "; ".join(failures[:5])

    return True, f"All {len(target_ids)} Important split emails with attachments have reminders set."
