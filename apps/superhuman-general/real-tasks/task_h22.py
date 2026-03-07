import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])

    # IDs of notification emails that were originally unread in inbox Other split
    originally_unread_ids = {25, 26, 115}
    # IDs of notification emails that were originally read in inbox Other split
    originally_read_ids = {27, 28, 30, 31, 33, 34, 36, 37, 39, 40, 41, 43,
                           84, 85, 86, 88, 90, 92, 95, 96, 98, 100, 116}

    email_map = {e.get("id"): e for e in emails}
    failures = []

    for eid in originally_read_ids:
        e = email_map.get(eid)
        if e is None:
            failures.append(f"Email id={eid} not found")
            continue
        if not e.get("isDone", False):
            failures.append(f"Read notification id={eid} '{e.get('subject','')}' not archived")

    for eid in originally_unread_ids:
        e = email_map.get(eid)
        if e is None:
            failures.append(f"Email id={eid} not found")
            continue
        if not e.get("isStarred", False):
            failures.append(f"Unread notification id={eid} '{e.get('subject','')}' not starred")

    if failures:
        return False, f"{len(failures)} issue(s): " + "; ".join(failures[:5])

    return True, "All read Other-split notifications archived and unread ones starred."
