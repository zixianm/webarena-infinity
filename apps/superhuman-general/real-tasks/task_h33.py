import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the Follow-up Needed label
    labels = state.get("labels", [])
    fu_label = None
    for l in labels:
        if "follow" in l.get("name", "").lower() and "needed" in l.get("name", "").lower():
            fu_label = l
            break
    if fu_label is None:
        for l in labels:
            if "follow-up" in l.get("name", "").lower() or "follow up" in l.get("name", "").lower():
                fu_label = l
                break

    if fu_label is None:
        return False, "No label matching 'Follow-up Needed' found."

    color = (fu_label.get("color") or "").lower()
    orange_colors = ["#ff9800", "#ff8f00", "#f57c00", "#ef6c00", "#e65100", "#ffa726", "#ffb74d", "#fb8c00", "orange"]
    if not any(o in color for o in orange_colors):
        return False, f"Label 'Follow-up Needed' color '{color}' does not appear to be orange."

    fu_id = fu_label["id"]

    # Check emails with reminders have the label
    reminder_email_ids = {64, 65, 66, 67, 111, 112}
    email_map = {e.get("id"): e for e in state.get("emails", [])}

    failures = []
    for eid in reminder_email_ids:
        e = email_map.get(eid)
        if e is None:
            failures.append(f"Email id={eid} not found")
            continue
        if fu_id not in e.get("labels", []):
            failures.append(f"Email id={eid} '{e.get('subject','')}' missing Follow-up Needed label")

    if failures:
        return False, f"{len(failures)} issue(s): " + "; ".join(failures[:5])

    return True, f"Label 'Follow-up Needed' (orange) exists and applied to all {len(reminder_email_ids)} reminder emails."
