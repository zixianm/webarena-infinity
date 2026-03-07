import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    emails = state.get("emails", [])

    # Find email with replyDraftingTeammate set
    target = None
    for e in emails:
        if e.get("replyDraftingTeammate"):
            target = e
            break

    if target is None:
        return False, "No email with a teammate drafting a reply found in state."

    failures = []

    if target.get("isDone", False):
        failures.append("Email is still in Done (archived) — should be moved to inbox (isDone=False).")

    work_label = None
    for l in state.get("labels", []):
        if l.get("name") == "Work":
            work_label = l
            break

    if work_label is None:
        failures.append("Work label not found in state.")
    else:
        if work_label["id"] not in target.get("labels", []):
            failures.append(f"Email is missing the 'Work' label. Current labels: {target.get('labels', [])}")

    if failures:
        return False, "; ".join(failures)

    return True, f"Email (id={target.get('id')}) with teammate draft moved to inbox and labeled 'Work'."
